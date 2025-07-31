from sklearn import svm, datasets
from scipy.spatial import distance
import time
import numpy as np
import MEArec as mr
from pathlib import Path
import MEAutility as mu
import LFPy
import sys

from MorphologyFunctions import *

mea_name = sys.argv[1]

# Load template
#templates_file = f'ziad_mearec_templates/mag_templates_flattened_morphology_L5_TTPC1_cADpyr232_1_n300_{mea_name}.h5'
#tempgen = mr.tools.load_templates(templates_file, verbose=False)

with open(f'./ziad_mearec_templates/mag_templates_flattened_morphology_L5_TTPC1_cADpyr232_1_n300_{mea_name}.npy', 'rb') as f:
    all_y = np.load(f)
    all_z = np.load(f)
    mags = np.load(f)

# Parameters
thresh = float(sys.argv[2])
snr = float(sys.argv[3])
iters_per_cell = int(sys.argv[4])
C = float(sys.argv[5])
gamma = sys.argv[6]
if gamma != 'default':
    gamma = float(sys.argv[6])

start_idx = 0
end_idx = len(mags)

segment = sys.argv[7]
quarter = int(len(mags)/4)
eighth = int(len(mags)/8)
if segment == 'Quarter1':
    end_idx = quarter
elif segment == 'Quarter2':
    start_idx = quarter
    end_idx = quarter*2
elif segment == 'Quarter3':
    start_idx = quarter*2
    end_idx = quarter*3
elif segment == 'Quarter4':
    start_idx = quarter*3
    end_idx = len(mags)

if 'Eighth' in segment:
    eighth_idx = int(segment[-1])-1
    start_idx = eighth_idx*eighth
    end_idx = start_idx + eighth
    if eighth_idx == 7:
        end_idx = len(mags)


print("Start, End: ", start_idx, end_idx)

cells = range(start_idx, end_idx)

# Main loop
elec_x, elec_y = get_electrodes2(mea_name)
xx, yy = make_meshgrid(np.array(elec_x), np.array(elec_y))

dists = np.zeros((len(cells), iters_per_cell))
dists_std = np.zeros((len(cells), iters_per_cell))
for n, template_id in enumerate(cells):
    print("Template ID: ", template_id)
    for itr in range(iters_per_cell):
        start = time.time()
        elec_x, elec_y = get_electrodes2(mea_name)

        #cell = load_cell(template_id, tempgen)
        noise = generate_noise(snr, mags[template_id], np.shape(mags[template_id]))
        coords, targets = get_strong_signals(mags[template_id] + noise, elec_x, elec_y, thresh)

        model = svm.SVC(kernel="rbf")
        clf = model.fit(coords, targets)

        boundary = get_boundary_coords(xx, yy, clf)
        if len(boundary) != 0:
            dist, std = get_apic_dist_real(template_id, all_y, all_z, xx, yy, clf, boundary = boundary)

        else:
            dist = 10000000
            std = 1000000

        print('Dist: ', dist)
        print('Std: ', std)
        dists[n, itr] = dist
        dists_std[n, itr] = std
        print("Time: ", time.time()-start)


for i in range(len(dists)):
    mean_total = 0
    var_total = 0
    count = 0
    for j in range(len(dists[0])):
        if dists[i, j] < 1000000:
            mean_total += dists[i, j]
            var_total += dists_std[i, j]**2
            count += 1
    mean_avg = ""
    std_avg = ""
    if count > 0:
        mean_avg = mean_total/count
        std_avg = np.sqrt(var_total/count) 
    print(mean_avg, '\t', std_avg, '\t', count)
