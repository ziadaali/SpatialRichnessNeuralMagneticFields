import numpy as np
import MEArec as mr
import MEAutility as mu
import os
import inspect
from pathlib import Path
import shutil
import pprint
import sys

import spikeinterface as si  # import core only
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import spikeinterface.widgets as sw

from spikeinterface.comparison import GroundTruthStudy
import time

from ziad_functions_spikesorting import *
from ziad_functions_submission import *

def grid_search(sorter, folder, keys, params, selected, study_folder_string, magnetic_dim = -1):
    #print(params)
    #print(selected)
    if len(params) == 0:
        kilosort2_params = ss.get_default_params(sorter)
        param_dict = {}
        for i in range(len(selected)):
            param_dict[keys[i]] = selected[i]
            kilosort2_params[keys[i]] = selected[i]
        print(param_dict)
        if isinstance(magnetic_dim, list):
            if isinstance(magnetic_dim[0], list):
                if magnetic_dim[0][-1] >= 0:
                    kilosort2_params['spkThPos'] = kilosort2_params['detect_threshold']
                    print("Enabled positive spike detection for: ", magnetic_dim)
            elif magnetic_dim[0] >= 0:
                kilosort2_params['spkThPos'] = kilosort2_params['detect_threshold']
                print("Enabled positive spike detection for: ", magnetic_dim)
            #elif isinstance(magnetic_dim[0], list):
            #    if magnetic_dim[0][-1] >= 0:
            #        kilosort2_params['spkThPos'] = kilosort2_params['detect_threshold']
            #        print("Enabled positive spike detection for: ", magnetic_dim)
        print("Kilosort2 Params: ", kilosort2_params)
        all_metrics, all_counts, failed_sorts = runSorterAll(sorter,
                                                             kilosort2_params,
                                                             folder,
                                                             delete=False,
                                                             verbose=False,
                                                             study_folder_string=study_folder_string,
                                                             magnetic_dim = magnetic_dim)
        grid_params.append(param_dict)
        grid_metrics.append(all_metrics)
        grid_counts.append(all_counts)
        grid_fails.append(failed_sorts)
        print("")
        return

    for j in range(len(params[0])):
        #print(params[i][j])
        new_selected = selected.copy()
        new_selected.append(params[0][j])
        #print(new_selected)
        grid_search(sorter, folder, keys, params[1:], new_selected, study_folder_string, magnetic_dim = magnetic_dim)



ss.Kilosort2Sorter.set_kilosort2_path('./Kilosort-2.0')

#magnetic_dims = [-1, 0, 1, 2, 3, 4, [3, 4], [1, 2], [0, 1, 2]]
#magnetic_dims = [-1, 0, 1, 2, 3, 4]
#magnetic_dims = [[3, 4], [1, 2], [0, 1, 2]]
#magnetic_dims = [-1, 0, 1, 2, [1, 2], [0, 1, 2]]
#magnetic_dims = [-1, 0, 1, 2]
#magnetic_dims = [[0, 1, 2]]
magnetic_dims = generate_field_list(sys.argv[3])

keys = ['detect_threshold', 'minFR', 'freq_min']
#vals = [[3, 4, 5, 6], [1.0, 2, 3], [150.0]]
#vals = [[3], [1.0], [150.0]]
#vals = [[3, 4, 5, 6], [0.25, 0.5], [150.0]]
vals = [[3, 4, 5, 6], [0.25, 0.5, 1.0], [150.0]]
#vals = [[1, 2], [0.25, 0.5, 1.0], [150.0]]
if sys.argv[6] == 'Half1':
    vals = [[3, 4], [0.25, 0.5, 1.0], [150.0]]
elif sys.argv[6] == 'Half2':
    vals = [[5, 6], [0.25, 0.5, 1.0], [150.0]]
elif 'Quarter' in sys.argv[6]:
    dthresh = 6
    if sys.argv[6] == 'Quarter1':
        dthresh = 3
    elif sys.argv[6] == 'Quarter2':
        dthresh = 4
    elif sys.argv[6] == 'Quarter3':
        dthresh = 5
    elif sys.argv[6] == 'Quarter4':
        dthresh = 6
    elif sys.argv[6] == 'Quarter2.5':
        dthresh = 2.5
    vals = [[dthresh], [0.25, 0.5, 1.0], [150.0]]
#vals = [[6], [1.0, 2, 3], [150.0]]
#vals = [[3], [0.5], [150.0]]

numcells = int(sys.argv[1])
duration = int(sys.argv[4])
noise = str(sys.argv[5])
far_neurons = 200
sorter = 'kilosort2'
make_mag_neg = False
study_folder_string = 'StudyFolder_' + sys.argv[1] + '_' + sys.argv[2] + '_' + sys.argv[3] + '_' + sys.argv[4] + '_' + sys.argv[5] + '_' + sys.argv[6]
print("Study Folder String: ", study_folder_string)

for magnetic_dim in magnetic_dims:
    print(f"STARTING GRID SEARCH FOR MAGNETIC_DIM: {magnetic_dim}")

    #folder = f'Mag_FullRot_{far_neurons}FarNeurons_{numcells}Cells_{duration}s_Noise{noise}_Train'
    folder = f'Mag_{sys.argv[2]}_{numcells}Cells_{duration}s_Noise{noise}_Train'
    #folder = f'Mag_Neuropixels128_radius50_{numcells}Cells_{duration}s_Noise{noise}_Train'
    #p = Path('/mnt/c/Users/Hong Lab/Spike_Interface_Test/MEArecRecordings/')
    #p = Path('/mnt/e/Ziad/MEArecRecordings/')
    #p = Path('./MEArecRecordings')
    p = Path('/scratch/groups/adapoon/ziad/SpikeSorting/')
    #deleteFolder(p / folder)

    grid_params = []
    grid_metrics = []
    grid_counts = []
    grid_fails = []

    mag_param = magnetic_dim
    if mag_param != -1:
        mag_param = [mag_param, make_mag_neg]
    grid_search(sorter, folder, keys, vals, [], study_folder_string, magnetic_dim = mag_param)

    for i in range(len(grid_params)):
        print(f"FINAL RESULTS FOR MAGNETIC_DIM {magnetic_dim}:")
        print(grid_params[i])
        avg_metrics, avg_counts = averageMetrics(grid_metrics[i], grid_counts[i])
        std_metrics, std_counts = stdMetrics(grid_metrics[i], grid_counts[i])
        pprint.pprint(avg_metrics)
        pprint.pprint(avg_counts)
        pprint.pprint(std_metrics)
        pprint.pprint(std_counts)
        print("Failed Sorts ", len(grid_fails[i]))
        fom = figureOfMerit(grid_metrics[i], grid_counts[i], len(grid_fails[i]), 2, 1)
        print("FoM: ", fom)
        print("")
