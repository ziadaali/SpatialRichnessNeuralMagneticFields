import numpy as np
import MEArec as mr
import MEAutility as mu
import os
import inspect
from pathlib import Path
import shutil
import pprint

import spikeinterface as si  # import core only
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import spikeinterface.widgets as sw

from spikeinterface.comparison import GroundTruthStudy
import time

main_file_num_cells = 0

def spikeSort(filename, study_folder, p, sorter, params, verbose, magnetic_dim = -1):
    # Delete data from previous spike sort
    deleteFolder(study_folder)

    mearec_filename = p / filename

    # Initialize recording and ground truth variables
    print("Spike Sort magnetic_dim: ", magnetic_dim)

    rec  = se.MEArecRecordingExtractor(mearec_filename, locs_2d=True, magnetic_dim = magnetic_dim)
    gt_sorting = se.MEArecSortingExtractor(mearec_filename)

    fs = rec.get_sampling_frequency()

    gt_dict = {}
    gt_dict[f'{filename}'] = (rec, gt_sorting)
    print("Creating Study")
    study = GroundTruthStudy.create(study_folder, gt_dict, magnetic_dim)
    print("Study created")
    sorter_list = ['kilosort2']

    sorter_params = {sorter: params}
    study.run_sorters(sorter_list, sorter_params=sorter_params, verbose=verbose)

    metrics, counts = getSortMetrics(study_folder)
    print("Metrics: ", metrics)
    print("Counts: ", counts)
    #raise ValueError("stop")
    return metrics, counts


def getSortMetrics(study_folder):
    study = GroundTruthStudy(study_folder)
    study.copy_sortings()
    study.run_comparisons(exhaustive_gt=True, match_score=0.1, overmerged_score=0.2)

    if len(study.aggregate_count_units()) == 0:
        print("No metrics - sorting failed")
        return {}, {}

    dataframes = study.aggregate_dataframes()
    perf = dataframes['perf_by_unit']
    count_units = dataframes['count_units']

    metric_keys = ['accuracy', 'recall', 'precision', 'false_discovery_rate', 'miss_rate']
    metrics = {}
    for key in metric_keys:
        metrics[f'{key}'] = np.mean(np.array(perf[f'{key}']))

    count_keys = ['num_gt', 'num_sorter', 'num_well_detected', 'num_redundant', 'num_overmerged', 'num_false_positive', 'num_bad']
    counts = {}
    for key in count_keys:
        counts[f'{key}'] = np.mean(np.array(count_units[f'{key}']))

    return metrics, counts


def initMetrics():
    all_metrics = {}
    all_counts = {}
    metric_keys = ['accuracy', 'recall', 'precision', 'false_discovery_rate', 'miss_rate']
    count_keys = ['num_gt', 'num_sorter', 'num_well_detected', 'num_redundant', 'num_overmerged', 'num_false_positive', 'num_bad']
    for metric in metric_keys:
        all_metrics[metric] = []
    for count in count_keys:
        all_counts[count] = []

    return all_metrics, all_counts


def updateMetrics(all_metrics, all_counts, metrics, counts):
    for key in metrics.keys():
        all_metrics[key].append(metrics[key])
    for key in counts.keys():
        all_counts[key].append(counts[key])
    return all_metrics, all_counts


def averageMetrics(all_metrics, all_counts):
    avg_metrics = {}
    avg_counts = {}
    for key in all_metrics.keys():
        avg = np.mean(np.array(all_metrics[key]))
        #print(key, avg)
        avg_metrics[key] = avg

    for key in all_counts.keys():
        avg = np.mean(np.array(all_counts[key]))
        #print(key, avg)
        avg_counts[key] = avg

    return avg_metrics, avg_counts

def stdMetrics(all_metrics, all_counts):
    std_metrics = {}
    std_counts = {}
    for key in all_metrics.keys():
        std = np.std(np.array(all_metrics[key]))
        std_metrics[key] = std

    for key in all_counts.keys():
        std = np.std(np.array(all_counts[key]))
        std_counts[key] = std

    return std_metrics, std_counts

def figureOfMerit(all_metrics, all_counts, failed_count, lambda1, lambda2):
    avg_metrics, avg_counts = averageMetrics(all_metrics, all_counts)
    metric_keys = ['accuracy', 'precision', 'recall']

    fom = 0
    for key in metric_keys:
        fom += (1 - avg_metrics[key])**2

    gt_count = avg_counts['num_gt']
    sorter_count = avg_counts['num_sorter']
    fom += lambda1*((gt_count - sorter_count)/gt_count)**2
    fom += lambda2*failed_count

    return fom


def sortFOM(grid_params):
    fom_keys = []
    fom_vals = []
    for i in range(len(grid_params)):
        #print(grid_params[i])
        avg_metrics, avg_counts = averageMetrics(grid_metrics[i], grid_counts[i])
        #pprint.pprint(avg_metrics)
        #pprint.pprint(avg_counts)
        #print("Failed Sorts ", len(grid_fails[i]))
        fom = figureOfMerit(grid_metrics[i], grid_counts[i], len(grid_fails[i]), 2, 1)
        #print("FoM: ", fom)
        #print("")
        if math.isnan(fom) == False:
            fom_keys.append(grid_params[i])
            fom_vals.append(fom)

    sorted_inds = np.array(fom_vals).argsort()
    sorted_fom_vals = [fom_vals[i] for i in sorted_inds]
    sorted_fom_keys = [fom_keys[i] for i in sorted_inds]

    return sorted_fom_vals, sorted_fom_keys


def deleteFolder(folder):
    # Delete folder if it exists
    try:
        shutil.rmtree(folder)
    except OSError as e:
        print("Error Deleting Directory: %s - %s." % (e.filename, e.strerror))


def folderExists(folder):
    cur_dir = '/scratch/groups/adapoon/ziad/SpikeSorting/'
    #cur_dir = '/mnt/e/Ziad/'
    path = os.path.join(cur_dir, f'MEArecRecordings/{folder}')
    if os.path.isdir(path):
        return True
    return False


def getLocalFileNames(folder):
    cur_dir = '/scratch/groups/adapoon/ziad/SpikeSorting/'
    #cur_dir = '/mnt/e/Ziad/'
    path = os.path.join(cur_dir, f'MEArecRecordings/{folder}')
    file_names = os.listdir(path)
    return file_names


def runSorterAll(sorter, params, folder, delete, verbose, study_folder_string, magnetic_dim = -1):
    #p = Path('/mnt/e/Ziad/MEArecRecordings/')
    p = Path('/scratch/groups/adapoon/ziad/SpikeSorting/MEArecRecordings')
    study_folder = p / study_folder_string
    print("Study Folder: ", study_folder)

    # Initialize dictionaries to store metrics
    all_metrics, all_counts = initMetrics()
    failed_sorts = []

    new_folder = f'{folder}'

    # If the folder of recording data already exists, just run sorter on all files in the folder
    if folderExists(folder):
        file_names = getLocalFileNames(folder)
        print("Local Files: ", file_names)
        for filename in file_names:

            metrics, counts = spikeSort(filename, study_folder, p / new_folder, sorter, params, verbose, magnetic_dim = magnetic_dim)
            if len(metrics.keys()) == 0:
                failed_sorts.append(filename)

            updateMetrics(all_metrics, all_counts, metrics, counts)

            print("")

    # If folder does not exist, download each file from Google Drive and process one at a time
    else:
        print('Missing Folder: ', folder)
        raise ValueError("Could not locate folder with recordings")

    return all_metrics, all_counts, failed_sorts
