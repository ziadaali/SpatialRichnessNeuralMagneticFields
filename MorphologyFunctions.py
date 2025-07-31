from sklearn import svm, datasets
from scipy.spatial import distance
import time
import numpy as np
import MEArec as mr
from pathlib import Path
import MEAutility as mu
import LFPy

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

def get_electrodes(mea_name):
    mea_cells_folder = '/Users/Ziad/.config/mearec/1.7.2/cell_models/MEArecLinearCells/'
    cell_name = 'L5_TTPC1_cADpyr232_1'
    cell_model_folder = Path(Path(mea_cells_folder) / cell_name)

    cell = mr.return_bbp_cell(cell_model_folder, end_T=1000, dt=0.03125, start_T=0)
    mea = mu.return_mea(mea_name)
    electrodes = LFPy.RecExtElectrode(cell, probe=mea)

    return electrodes

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

def plot_contours(ax, clf, xx, yy, **params):
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    out = ax.contourf(xx, yy, Z, **params)
    return out

def load_cell(template_id, tempgen):
    # Load cell and position and rotation info
    mea_cells_folder = '/Users/Ziad/.config/mearec/1.7.2/cell_models/MEArecLinearCells/'
    cell_name = 'L5_TTPC1_cADpyr232_1'
    cell_model_folder = Path(Path(mea_cells_folder) / cell_name)

    T = 1000
    dt = 0.03125
    cell = mr.return_bbp_cell(cell_model_folder, end_T=T, dt=dt, start_T=0)

    pos = tempgen.locations[template_id]
    rot = tempgen.rotations[template_id]

    cell = mr.ziad_flatten_geometry(cell, pos, rot, 10)
    cell.set_pos(pos[0], pos[1], pos[2])
    cell.set_rotation(rot[0], rot[1], rot[2])

    return cell

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

    return np.mean(dists), np.std(dists)

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

    print("SNR: ", 10*np.log10(sig_pwr/noise_pwr))
    return noise
