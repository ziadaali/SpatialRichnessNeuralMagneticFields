import MEArecGenerate as mr
import numpy as np
import matplotlib.pyplot as plt
import MEAutility as mu
#import LFPy
from matplotlib.collections import LineCollection
#from neuron import h
import os
import inspect
from pathlib import Path
import shutil
import sys

def generate_single_recording(numcells, duration, noise, noise_setting, gdrive_folder, local_template_folder):
    #folder_id = get_folder_id(gdrive_folder) #Gets Google Drive folder ID

    rec_params = mr.get_default_recordings_params()
    rec_params['cell_types'] = {'excitatory': ['exc'], 'inhibitory': ['inh']}

    rec_params['spiketrains']['duration'] = duration # number of seconds to generate for
    rec_params['spiketrains']['n_exc'] = numcells # number of excitatory cells (randomly selected) to simulate
    rec_params['spiketrains']['n_inh'] = 0 # number of inhibitory cells (randomly selected) to simulate
    rec_params['templates']['min_dist'] = 1 # minimum distance cells must be from each other in um
    rec_params['templates']['min_amp'] = 30 # minimum amplitude? not sure what this is for
    rec_params['templates']['max_amp'] = 400
    rec_params['recordings']['noise_level'] = noise # noise level added in background

    rec_params['recordings']['mag_noise'] = noise_setting

    recgen = mr.gen_recordings(params=rec_params, templates=local_template_folder, verbose=True, magnetic=True)

    return recgen

def generate_recording_files(numcells, duration, noise, noise_setting, count, gdrive_folder, local_template_folder):
    #folder_id = get_folder_id(gdrive_folder) #Gets Google Drive folder ID

    for i in range(0, count):
        recgen = generate_single_recording(numcells, duration, noise, noise_setting, gdrive_folder, local_template_folder)

        filename = f'{gdrive_folder}/all_recordings_{numcells}cells_{duration}s_noise{noise}_{i}.h5'
        print("Saving recgen")
        mr.save_recording_generator(recgen=recgen, filename=filename)

def get_delta_from_filename(filename):
    idx1 = filename.index('cells') + 6
    idx2 = filename.index('delta')
    return filename[idx1:idx2]

def get_mea_from_filename(filename):
    idx1 = filename.rfind('_') + 1
    idx2 = filename.rfind('.')
    return filename[idx1:idx2]

all_numcells = [2]
#all_numcells = [60, 80]
#all_numcells = [20]
all_durations = [int(sys.argv[2])]
all_noise = [int(sys.argv[3])]
#noise_setting = 'equalize_avg_power'
noise_setting = sys.argv[1]
#template_folder = f'ziad_mearec_templates/mag_templates_2-4cells_n50_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_test_2-3cells_n3_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_fullrot_2-4cells_n50_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n250_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_radius50_2-4cells_n150_Neuropixels-128.h5'
template_folder = sys.argv[4]
delta = get_delta_from_filename(template_folder)
mea = get_mea_from_filename(template_folder)
# recgen = generate_single_recording(all_numcells[0],
#                                    all_durations[0],
#                                    all_noise[0],
#                                    noise_setting,
#                                    f'Mag_{all_numcells[0]}Cells_{all_durations[0]}s_Noise{all_noise[0]}_Train',
#                                    template_folder)

for numcells in all_numcells:
    for duration in all_durations:
        for noise in all_noise:
            count = 5

            generate_recording_files(numcells,
                         duration,
                         noise,
                         noise_setting,
                         count,
                         f'/scratch/groups/adapoon/ziad/SpikeSorting/MEArecRecordings/Mag_{mea}_{delta}Delta_{noise_setting}_{numcells}Cells_{duration}s_Noise{noise}_Train',
                         template_folder)
