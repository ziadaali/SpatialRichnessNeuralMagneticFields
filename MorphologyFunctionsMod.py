from sklearn import svm, datasets
from scipy.spatial import distance
import numpy as np

# Get all signals from the grid of electrodes that exceed a certain threshold
def get_strong_signals(data, elec_x, elec_y, thresh):
    data = data/np.max(abs(data))
    
    coords = []
    targets = []
    for i in range(len(data)):
        if np.max(abs(data[i])) >= thresh:
            coords.append([elec_x[i], elec_y[i]])
            
            # Target is 1 if signal is positive, 0 if negative
            targets.append(np.max(data[i]) > abs(np.min(data[i])))
            
    return np.array(coords), np.array(targets)

def get_electrodes2(mea_name):
    m_idx = mea_name.find('MEA')
    count = int(np.sqrt(int(mea_name[:m_idx])))
    pitch = int(mea_name[m_idx+3:])
    
    max_coord = (count - 1)*pitch/2.0
    coords = np.arange(-1*max_coord, max_coord+1, pitch)
    
    elec_x = []
    elec_y = []
    for xcoord in coords:
        for ycoord in coords:
            elec_x.append(xcoord)
            elec_y.append(ycoord)
    
    return np.array(elec_x), np.array(elec_y)

def make_meshgrid(x, y, h=.5):
    x_min, x_max = x.min() - 1, x.max() + 1
    y_min, y_max = y.min() - 1, y.max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    return xx, yy

def get_apic_dist(template_id, all_y, all_z, clf, verbose=False):
    coords = np.zeros((2, np.shape(all_y)[1]))
    coords[0] = all_y[template_id]
    coords[1] = all_z[template_id]
    dists = abs(clf.decision_function(coords.T))/np.linalg.norm(clf.coef_)
    if verbose:
        print(dists)
    
    return np.mean(dists), np.std(dists)

def get_apic_dist_real(template_id, all_y, all_z, xx, yy, clf, boundary = [], verbose=False):
    coords = np.zeros((np.shape(all_y)[1], 2))
    coords[:, 0] = all_y[template_id]
    coords[:, 1] = all_z[template_id]
    
    if len(boundary) == 0:
        dists = distance.cdist(coords, get_boundary_coords(xx, yy, clf), 'euclidean')
    else:
        dists = distance.cdist(coords, boundary, 'euclidean')
        
    dists = np.min(dists, axis=1)
    if verbose:
        print(dists)
        plt.hist(dists, bins=30)
        
    return np.mean(dists), np.std(dists), dists

def get_boundary_coords(xx, yy, clf):
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    boundary = []
    for i in range(len(xx)):
        for j in range(1, len(xx[0])):
            if j > 0:
                if Z[i, j] != Z[i, j-1]:
                    #print("hit1")
                    midx = (xx[i, j] + xx[i, j-1]) / 2
                    midy = yy[i, j]
                    boundary.append([midx, midy])
            if i > 0:
                if Z[i, j] != Z[i-1, j]:
                    #print("hit2")
                    midx = xx[i, j]
                    midy = (yy[i, j] + yy[i-1, j]) / 2
                    boundary.append([midx, midy])
    #print(boundary)
    boundary = np.array(boundary)
    return boundary

def generate_noise(snr, sig, shape):
    noise = np.random.normal(size=shape)
    
    sig_pwr = np.sum(sig**2)
    noise_pwr = sig_pwr/(10**(snr/10))
    noise_coeff = np.sqrt(noise_pwr/np.sum(noise**2))
    noise = noise*noise_coeff
    
    new_noise_pwr = np.sum(noise**2)
    
    #print("SNR: ", 10*np.log10(sig_pwr/noise_pwr))
    return noise

def estimate_axon_hillock(signals, elec_x, elec_y, return_med = False):
    mags_pwr = np.sqrt(np.sum(signals**2, axis=1))
    mags_strong_indices = np.argsort(-1*mags_pwr)[:4]
    
    mags_relative_pwr = mags_pwr[mags_strong_indices] / np.sum(mags_pwr[mags_strong_indices])

    new_x = np.sum(elec_x[mags_strong_indices] * mags_relative_pwr)
    new_y = np.sum(elec_y[mags_strong_indices] * mags_relative_pwr)
    
    # Returns coordinates of other strong points
    if return_med:
        new_coords = []
        indices = np.arange(10, 100, 10)
        for index in indices:
            mags_med_indices = np.argsort(-1*mags_pwr)[index:index+4]

            mags_relative_pwr_med = mags_pwr[mags_med_indices] / np.sum(mags_pwr[mags_med_indices])

            med_x = np.sum(elec_x[mags_med_indices] * mags_relative_pwr_med)
            med_y = np.sum(elec_y[mags_med_indices] * mags_relative_pwr_med)
            
            new_coords.append([med_x, med_y])
        
        return new_x, new_y, np.array(new_coords)
    
    return new_x, new_y

def gen_modified_coords(clf, signals, elec_x, elec_y, xx, yy, coords, targets, params):
    
    min_dist = params['min_dist']
    max_dist = params['max_dist']
    num_points = params['num_points']
    
    opp_dist = params['opp_dist']
    
    # Get boundary estimation (true/false values assigned to dense coordinate map) and cast to boolean
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    Z = (Z != 0)
    
    # Estimate axon hillock as well as direction of neuron
    ah_x, ah_y, new_coords = estimate_axon_hillock(signals, elec_x, elec_y, return_med = True)
    
    # Calculate line of best fit - assign half the points to be identical (axon hillock)
    mult = 2
    fit_coords = np.zeros((len(new_coords)*(mult+1), 2))
    fit_coords[:len(new_coords)*mult, 0] = ah_x
    fit_coords[:len(new_coords)*mult, 1] = ah_y
    fit_coords[len(new_coords)*mult:, 0] = new_coords[:, 0]
    fit_coords[len(new_coords)*mult:, 1] = new_coords[:, 1]
    m, b = np.polyfit(fit_coords[:, 0], fit_coords[:, 1], 1)
    
    # Find points above line
    q = yy > (xx*m + b)
    
    # Determine whether points above line are mostly in category 0 or 1 of SVM
    greater_than_category = np.sum(q & Z)/np.sum(q) > 0.5
    
    # Generate points close to axon_hillock along line of best fit at specified distances
    nearby_dists = np.linspace(min_dist, max_dist, num_points)

    # Find closest point to (ah_x, ah_y) on line
    b2 = ah_y + ah_x/m
    ah_x2 = (b2 - b)/(m + 1/m)
    ah_y2 = m*ah_x2 + b

    # Get nearby points along line of best fit
    nearby_x = nearby_dists/np.sqrt(1 + m**2) + ah_x2
    nearby_y = m*nearby_x + b

    # Get one point one either side of each of those points along the line perpendicular to line of best fit
    b_vals = nearby_y + nearby_x/m
    opposite_dists = np.arange(-1*opp_dist, opp_dist + 0.1, 2*opp_dist)
    opposite_x = np.add.outer(opposite_dists/np.sqrt(1 + (1/m)**2), nearby_x)
    b_vals = np.ones(np.shape(opposite_x)) * b_vals
    opposite_y = -1*opposite_x / m + b_vals

    # Generate modified coordinates and targets
    mod_coords = np.zeros((len(coords)+np.shape(opposite_x)[1]*np.shape(opposite_x)[0], 2))
    mod_coords[:len(coords), :] = coords
    mod_coords[len(coords):len(coords)+len(opposite_x[0]), 0] = opposite_x[0, :]
    mod_coords[len(coords):len(coords)+len(opposite_x[0]), 1] = opposite_y[0, :]
    mod_coords[len(coords) + len(opposite_x[0]):len(coords)+len(opposite_x[0])*2, 0] = opposite_x[1, :]
    mod_coords[len(coords) + len(opposite_x[0]):len(coords)+len(opposite_x[0])*2, 1] = opposite_y[1, :]

    mod_targets = np.zeros((len(mod_coords),))
    mod_targets[:len(targets)] = targets[:]
    mod_targets[len(targets):np.shape(opposite_x)[1] + len(targets)] = not greater_than_category
    mod_targets[len(targets) + np.shape(opposite_x)[1]:np.shape(opposite_x)[1]*2 + len(targets)] = greater_than_category

    return mod_coords, mod_targets

