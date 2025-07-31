import numpy as np
import matplotlib.pyplot as plt
import MEAutility as mu
import time
from ZIAD_MEARotation_Functions import *
import sys

print('Beginning Rotation-Translation Script')

# Load MEA data
folder_name = '/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/'
#mea_name = '2250000MEA2'
#mea_name = '100MEA75'
mea_name = sys.argv[1]
cell_ids = sys.argv[2]
cell_id1 = cell_ids[0]
cell_id2 = cell_ids[1]

# Fields to calculate
str_fields = sys.argv[11]
sel_fields = []
for i in range(len(str_fields)):
    sel_fields.append(int(str_fields[i]))

file_name = f'mag_templates_flattened_cell{cell_id1}_origin_{mea_name}.npy'

with open(folder_name + file_name, 'rb') as f:
    v = np.load(f)[:, :, :]
    bx = np.load(f)[:, :, :]
    by = np.load(f)[:, :, :]
    bz = np.load(f)[:, :, :]
    locs = np.load(f)
    rots = np.load(f)

v1 = v[0]
bx = bx[0]
by = by[0]
bz = bz[0]

B1 = np.zeros((np.shape(bx)[0], np.shape(bx)[1], 3))
B1[:, :, 0] = by
B1[:, :, 1] = bz
B1[:, :, 2] = bx

file_name = f'mag_templates_flattened_cell{cell_id2}_origin_{mea_name}.npy'

with open(folder_name + file_name, 'rb') as f:
    v = np.load(f)[:, :, :]
    bx = np.load(f)[:, :, :]
    by = np.load(f)[:, :, :]
    bz = np.load(f)[:, :, :]
    locs = np.load(f)
    rots = np.load(f)

v2 = v[0]
bx = bx[0]
by = by[0]
bz = bz[0]

B2 = np.zeros((np.shape(bx)[0], np.shape(bx)[1], 3))
B2[:, :, 0] = by
B2[:, :, 1] = bz
B2[:, :, 2] = bx


# Set rotation angles
theta_arg = sys.argv[3]
sub_idx1 = theta_arg.index('_')
sub_idx2 = theta_arg.index('_', sub_idx1+1)
num_thetas = int(theta_arg[:sub_idx1])
theta_idx1 = int(theta_arg[(sub_idx1+1):sub_idx2])
theta_idx2 = int(theta_arg[(sub_idx2+1):])

thetas = np.linspace(0, 2*np.pi, num_thetas)
thetas = thetas[theta_idx1:theta_idx2]
k = int(sys.argv[4])

# Get 2D y-z coordinates
mu.add_mea(mea_name + '.yaml')
mea = mu.return_mea(mea_name)
coords = mea.positions[:, 1:]
col_coords = np.unique(coords[:, 0])
row_coords = np.unique(coords[:, 1])
X, Y = np.meshgrid(col_coords, row_coords)

# Set translation values
x_steps = int(sys.argv[5])
y_steps = int(sys.argv[6])
x_trans = np.linspace(int(sys.argv[7]), int(sys.argv[8]), x_steps)
y_trans = np.linspace(int(sys.argv[9]), int(sys.argv[10]), y_steps)

v_corrs = np.zeros((len(thetas), x_steps, y_steps))
b_corrs = np.zeros((len(thetas), 3, x_steps, y_steps))

b_fields = ['Bx', 'By', 'Bz']

for n, theta in enumerate(thetas):

    # Get rotated coordinates
    new_coords = rotate_matrix(theta, coords)

    # Find knn
    print("Finding k-nearest neighbors")
    k_nn, k_nn_dists = find_k_nn3(new_coords, coords, row_coords, col_coords, k)

    if 0 in sel_fields:
        rot_v_pred = rotate_scalar_field(k_nn, k_nn_dists, v2)
        print("Finished v_pred")
    if 1 in sel_fields or 2 in sel_fields or 3 in sel_fields:
        rot_B_pred = rotate_vector_field(k_nn, k_nn_dists, B2, theta)
        print("Finished b_pred")

    print("Theta: ", theta)

    for x, x_translation in enumerate(x_trans):
        for y, y_translation in enumerate(y_trans):

            idxs_grab, idxs_place = get_grab_place_idxs(coords, col_coords, row_coords, x_translation, y_translation)
            
            if 0 in sel_fields:
                new_v = np.zeros(np.shape(v1))

                new_v[idxs_place] = rot_v_pred[idxs_grab]

                v_corr = np.sum(new_v * v1) / (np.linalg.norm(new_v) * np.linalg.norm(v1))
                v_corrs[n, x, y] = v_corr
                print("V Correlation: ", v_corr)

            for i in range(3):
                if (i+1) in sel_fields:
                    new_B = np.zeros(np.shape(B1[:, :, i]))
                    new_B[idxs_place] = rot_B_pred[idxs_grab, :, i]
                    b_corr = np.sum(new_B * B1[:, :, i]) / (np.linalg.norm(new_B) * np.linalg.norm(B1[:, :, i]))
                    b_corrs[n, i, x, y] = b_corr
                    print(b_fields[i], "Correlation: ", b_corr)

print("v_corrs mean: ", np.mean(v_corrs))
print("b_corrs mean: ", np.mean(b_corrs[:, 0]), np.mean(b_corrs[:, 1]), np.mean(b_corrs[:, 2]))

save_folder = '/home/groups/adapoon/ziad/SpikeSorting/CorrelationOutput/'

save_file = 'TranslationRotationData'
for i in range(1,11):
    save_file += f'_{sys.argv[i]}'
save_file += '.npy'

with open(save_folder + save_file, 'wb') as f:
    np.save(f, v_corrs)
    np.save(f, b_corrs)




