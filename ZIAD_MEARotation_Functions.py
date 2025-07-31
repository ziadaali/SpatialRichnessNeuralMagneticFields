import numpy as np
import MEAutility as mu

def rotate_matrix(theta, coords):
    rot_matrix = np.zeros((2, 2))
    rot_matrix[0, 0] = np.cos(theta)
    rot_matrix[0, 1] = np.sin(theta)
    rot_matrix[1, 0] = -np.sin(theta)
    rot_matrix[1, 1] = np.cos(theta)

    new_coords = rot_matrix @ coords.T
    new_coords = new_coords.T

    return new_coords

def generate_coords(rows, cols, pitch):
    row_coords = np.arange(-0.5*pitch*(rows-1), 0.5*pitch*(rows-1)+0.01, pitch)
    col_coords = np.arange(-0.5*pitch*(cols-1), 0.5*pitch*(cols-1)+0.01, pitch)

    coords = np.zeros((rows*cols, 2))

    n = 0
    for x in col_coords:
        for y in row_coords:
            coords[n] = [x, y]
            n += 1

    return coords, row_coords, col_coords

def find_k_nn(new_coords, old_coords, k):

    # Find distance of each old_coordinate from each new_coordinate - row is old_coord, col is new_coord
    dists = np.linalg.norm(new_coords - old_coords[:, None], axis=2)

    k_nn = np.zeros((len(new_coords), k))
    k_nn_dists = np.zeros((len(new_coords), k))

    for i in range(len(new_coords)):
        nn = np.argpartition(dists[i], k)
        nn = nn[:k]
        #print("nn: ", nn)
        k_nn[i] = nn
        k_nn_dists[i] = dists[i, nn]

    return k_nn, k_nn_dists

def find_k_nn2(new_coords, old_coords, k):

    k_nn = np.zeros((len(new_coords), k))
    k_nn_dists = np.zeros((len(new_coords), k))

    # Find distance of each old_coordinate from each new_coordinate - row is old_coord, col is new_coord
    last_frac = 0
    for i in range(len(old_coords)):

        # Check progress
        if i > len(old_coords) / 10 * last_frac:
            print("Completed: ", 10*last_frac, "%")
            last_frac += 1

        dists = np.linalg.norm(new_coords - old_coords[i:i+1, None], axis=2)
        nn = np.argpartition(dists[0], k)
        nn = nn[:k]
        k_nn[i] = nn
        k_nn_dists[i] = dists[0, nn]

    return k_nn, k_nn_dists

def find_k_nn3(new_coords, old_coords, row_coords, col_coords, k):

    k_nn = np.zeros((len(new_coords), k))
    k_nn_dists = np.zeros((len(new_coords), k))

    row_coords_start = row_coords[0]
    col_coords_start = col_coords[0]

    dx = col_coords[1] - col_coords[0]
    dy = row_coords[1] - row_coords[0]

    last_frac = 0
    for idx in range(len(new_coords)):

        # Check progress
        if idx > len(old_coords) / 10 * last_frac:
            print("Completed: ", 10*last_frac, "%")
            last_frac += 1

        # Find distance of select new_coord from each x value of old_coords, select top k
        dist = np.linalg.norm(new_coords[idx:idx+1, 0] - col_coords[:, None], axis=1)
        a = np.argpartition(dist, k)
        xargs = a[:k]

        # Find distance of select new_coord from each y value of old_coords
        dist = np.linalg.norm(new_coords[idx:idx+1, 1] - row_coords[:, None], axis=1)
        a = np.argpartition(dist, k)
        yargs = a[:k]

        # Combine x and y into each pair-wise pair
        xargs, yargs = np.meshgrid(xargs, yargs)
        xargs = xargs.flatten()
        yargs = yargs.flatten()

        # Convert x and y args to idxs and get corresponding "close coordinates" (smaller subset)
        close_coords_idxs = xargs*len(col_coords) + yargs
        close_coords = old_coords[close_coords_idxs]

        # Get distance from select new_coord to each close_coord
        dists = np.linalg.norm(new_coords[idx:idx+1] - close_coords[:], axis=1)
        a = np.argpartition(dists, k)
        a = a[:k]
        close_coords = close_coords[a]
        close_coords[:, 0] = ((close_coords[:, 0] - col_coords_start) / dx)
        close_coords[:, 1] = ((close_coords[:, 1] - row_coords_start) / dy)

        # Index stored is transpose of actual index because converted to get dist from each old_coord
        i = int((idx % len(col_coords)) * len(col_coords) + np.floor(idx / len(col_coords)))
        temp = close_coords[:, 1]*len(col_coords) + close_coords[:, 0]
        k_nn[i] = temp
        k_nn_dists[i] = dists[a]

    return k_nn, k_nn_dists

def rotate_scalar_field(k_nn, k_nn_dists, vals):

    new_vals = np.zeros(np.shape(vals))
    weights = 1/k_nn_dists
    weights = weights/np.expand_dims(np.sum(weights, axis=1), axis=1)

    # Correct for dividing by zero
    nan_weights = np.argwhere(np.isnan(weights))
    weights[nan_weights] = 1

    last_frac = 0
    for i in range(len(new_vals)):
#         if i > len(new_vals) / 10 * last_frac:
#             print("Completed: ", 10*last_frac, "%")
#             last_frac += 1
        for j, idx in enumerate(k_nn[i]):
            new_vals[i] += vals[int(idx)]*weights[i, j]

    return new_vals

def rotate_vector_field(k_nn, k_nn_dists, vals, theta):

    new_vals = rotate_scalar_field(k_nn, k_nn_dists, vals)

    rot_matrix = np.zeros((3, 3))
    rot_matrix[0, 0] = np.cos(theta)
    rot_matrix[0, 1] = np.sin(theta)
    rot_matrix[1, 0] = -np.sin(theta)
    rot_matrix[1, 1] = np.cos(theta)
    rot_matrix[2, 2] = 1

    rot_new_vals = np.zeros(np.shape(new_vals))

    for i in range(np.shape(new_vals)[1]):
        temp = rot_matrix @ new_vals[:, i].T
        rot_new_vals[:, i] = temp.T

    return rot_new_vals

def get_grab_place_idxs(coords, col_coords, row_coords, x_translation, y_translation):

    xmin = np.min(col_coords)
    xmax = np.max(col_coords)
    ymin = np.min(row_coords)
    ymax = np.max(row_coords)

    # Get bounds for sub-region to translate
    if x_translation > 0:
        xbound_min = xmin
        xbound_max = xmax - x_translation

        xbound_min_place = xmin + x_translation
        xbound_max_place = xmax
    else:
        xbound_min = xmin - x_translation
        xbound_max = xmax

        xbound_min_place = xmin
        xbound_max_place = xmax + x_translation

    if y_translation > 0:
        ybound_min = ymin
        ybound_max = ymax - y_translation

        ybound_min_place = ymin + y_translation
        ybound_max_place = ymax
    else:
        ybound_min = ymin - y_translation
        ybound_max = ymax

        ybound_min_place = ymin
        ybound_max_place = ymax + y_translation

    # Get idxs of corresponding coordinates
    idxs_grab = np.where((coords[:, 1] >= ybound_min) & (coords[:, 1] <= ybound_max) & (coords[:, 0] >= xbound_min) & (coords[:, 0] <= xbound_max))[0]
    idxs_place = np.where((coords[:, 1] >= ybound_min_place) & (coords[:, 1] <= ybound_max_place) & (coords[:, 0] >= xbound_min_place) & (coords[:, 0] <= xbound_max_place))[0]

    return idxs_grab, idxs_place
