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

def generate_single_recording(numcells, duration, noise, noise_setting, gdrive_folder, local_template_folder, noise_mode = '', far_neurons = 0, noise_template_folder='', bursting_setting=False):
    #folder_id = get_folder_id(gdrive_folder) #Gets Google Drive folder ID

    rec_params = mr.get_default_recordings_params()
    rec_params['cell_types'] = {'excitatory': ['exc'], 'inhibitory': ['inh']}

    rec_params['spiketrains']['duration'] = duration # number of seconds to generate for
    rec_params['spiketrains']['n_exc'] = numcells # number of excitatory cells (randomly selected) to simulate
    rec_params['spiketrains']['n_inh'] = 0 # number of inhibitory cells (randomly selected) to simulate
    rec_params['templates']['min_dist'] = 1 # minimum distance cells must be from each other in um
    rec_params['templates']['min_amp'] = 1 # minimum amplitude? not sure what this is for
    rec_params['templates']['max_amp'] = 400
    if 'MEA' in gdrive_folder:
        rec_params['templates']['max_amp'] = 1500
    rec_params['recordings']['noise_level'] = noise # noise level added in background
    rec_params['recordings']['bursting'] = bursting_setting # Whether to include bursting in spike train

    print("Bursting setting: ", bursting_setting)
    #Testing filtering
    rec_params['recordings']['filter'] = False

    rec_params['recordings']['mag_noise'] = noise_setting
    if noise_mode == 'ziad-far-neurons':
        rec_params['recordings']['noise_mode'] = 'ziad-far-neurons'
        rec_params['recordings']['far_neurons_n'] = far_neurons
        recgen = mr.gen_recordings(params=rec_params, templates=local_template_folder, verbose=True, magnetic=True, noise_templates=noise_template_folder)
    else:
        recgen = mr.gen_recordings(params=rec_params, templates=local_template_folder, verbose=True, magnetic=True)

    return recgen

def generate_recording_files(numcells, duration, noise, noise_setting, count, gdrive_folder, local_template_folder, noise_template_folder, noise_mode='', far_neurons=0, bursting_setting=False):
    #folder_id = get_folder_id(gdrive_folder) #Gets Google Drive folder ID

    for i in range(0, count):
        recgen = generate_single_recording(numcells, duration, noise, noise_setting, gdrive_folder, local_template_folder, noise_mode=noise_mode, far_neurons=far_neurons,noise_template_folder=noise_template_folder,bursting_setting=bursting_setting)
        noise_string = ''
        if noise_mode == 'ziad-far-neurons':
            noise_string = f'_{noise_mode}'

        filename = f'{gdrive_folder}/all_recordings{noise_string}_{numcells}cells_{duration}s_noise{noise}_{i}.h5'
        print("Saving recgen")
        mr.save_recording_generator(recgen=recgen, filename=filename)

def get_mea_from_filename(filename):
    idx1 = filename.rfind('_') + 1
    idx2 = filename.rfind('.')
    return filename[idx1:idx2]

def get_radius_from_filename(filename):
    radius_idx = filename.find('_radius')
    if radius_idx < 0:
        return ""
    end_idx = filename.find('_', radius_idx+1)
    return filename[radius_idx:end_idx]

#all_numcells = [100]
#all_numcells = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
#all_numcells = [40, 80, 120, 160, 200, 300, 400, 500]
all_numcells = [20]
#all_numcells = [120, 140, 160, 180, 200]
#all_numcells = [20, 40, 60, 80, 100]
#all_numcells = [60, 80]
#all_numcells = [20]
all_durations = [int(sys.argv[2])]
all_noise = [float(sys.argv[3])]
#noise_setting = 'equalize_avg_power'
noise_setting = sys.argv[1]
#template_folder = f'ziad_mearec_templates/mag_templates_2-4cells_n50_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_test_2-3cells_n3_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_fullrot_2-4cells_n50_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n250_100MEA75.h5'
#template_folder = f'ziad_mearec_templates/mag_templates_radius50_2-4cells_n150_Neuropixels-128.h5'
template_folder = sys.argv[4]
mea = get_mea_from_filename(template_folder)
radius = get_radius_from_filename(template_folder)

noise_mode = sys.argv[5]
far_neurons = int(sys.argv[6])
noise_template_folder = sys.argv[7]
noise_radius = get_radius_from_filename(noise_template_folder)
noise_radius = noise_radius[1:]
noise_radius = f'_noise{noise_radius}'
if noise_mode != 'ziad-far-neurons':
    noise_radius = ""
else:
    noise_radius = f'{noise_radius}_far-neurons{far_neurons}'

bursting_setting = sys.argv[8]
if bursting_setting == "False":
    bursting_setting = False
else:
    bursting_setting = True

# recgen = generate_single_recording(all_numcells[0],
#                                    all_durations[0],
#                                    all_noise[0],
#                                    noise_setting,
#                                    f'Mag_{all_numcells[0]}Cells_{all_durations[0]}s_Noise{all_noise[0]}_Train',
#                                    template_folder)

for numcells in all_numcells:
    for duration in all_durations:
        for noise in all_noise:
            count = 10
            save_folder = f'/scratch/groups/adapoon/ziad/SpikeSorting/MEArecRecordings/Mag_{mea}{radius}{noise_radius}_SomaFlattened-{noise_setting}_Bursting-{bursting_setting}_{noise_mode}_{numcells}Cells_{duration}s_Noise{noise}_Train'
            print("Save folder: ", save_folder)
            #raise ValueError('Stop for testing')

            generate_recording_files(numcells,
                         duration,
                         noise,
                         noise_setting,
                         count,
                         save_folder,
                         template_folder,
                         noise_template_folder,
                         noise_mode=noise_mode,
                         far_neurons=far_neurons,
                         bursting_setting=bursting_setting)
