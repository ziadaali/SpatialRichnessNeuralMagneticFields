import numpy as np
import MEArec as mr
import MEAutility as mu
import os

import spikeinterface as si
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import spikeinterface.widgets as sw

from spikeinterface.comparison import GroundTruthStudy
import time

file_name = '/home/groups/adapoon/ziad/SpikeSorting/MEArecRecordings/test/all_recordings_10cells_20s_noise5_9.h5'

print("Beginning Ground Truth Study")

rec0  = se.MEArecRecordingExtractor(file_name)
gt_sorting0 = se.MEArecSortingExtractor(file_name)

gt_dict = {'rec0' : (rec0, gt_sorting0) }

ss.Kilosort2Sorter.set_kilosort2_path('./Kilosort-2.0')
sorter_list = ['kilosort2']
#study_folder = '/home/groups/adapoon/ziad/SpikeSorting/MEArecRecordings/test/StudyFolder'
study_folder = '/home/users/ziadaali/SpikeSorting/StudyFolder'
study = GroundTruthStudy.create(study_folder, gt_dict)
study = GroundTruthStudy(study_folder)
sorter_params = ss.get_default_params(sorter_list[0])
sorter_params['filter'] = False 

study.run_sorters(sorter_list, sorter_params=sorter_params, verbose=True)
