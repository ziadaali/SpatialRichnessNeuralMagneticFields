import os
from datetime import date
from ziad_functions_submission import generate_field_list

# Fill in these parameters for every run
mea_name = '400MEA50'

#threshs = [0, 0.001, 0.005]
threshs = [0]

snrs = [40]
#snrs = [0]

iters_per_cell = 1
Cs = [1.0]
gammas = ['default']

#segments = ['Quarter1', 'Quarter2', 'Quarter3', 'Quarter4']
#segments = ['Eighth1', 'Eighth2', 'Eighth3', 'Eighth4', 'Eighth5', 'Eighth6', 'Eighth7', 'Eighth8']
#segments = ['Eighth1', 'Eighth2', 'Eighth3', 'Eighth4']
#segments = ['Eighth2', 'Eighth4', 'Eighth6', 'Eighth7', 'Eighth8']
#segments = ['Eighth5']
segments = ['All']

min_max_dists = [[-50, 50], [-25, 25], [-10, 10], [-50, 25]]
num_points = [100, 50, 25]
opp_dists = [2, 5, 10, 25]

def create_submit_script(thresh, snr, C, gamma, segment, min_max, num_point, opp_dist):
    date_string = str(date.today().month) + '_' + str(date.today().day)
    with open('submit_mod_morphology_template.sh', 'rt') as fin:
        with open('submit_mod_morphology_script.sh', 'wt') as fout:
            for line in fin:
                new_line = line.replace('%mea%', str(mea_name))
                new_line = new_line.replace('%thresh%', str(thresh))
                new_line = new_line.replace('%snr%', str(snr))
                new_line = new_line.replace('%iters%', str(iters_per_cell))
                new_line = new_line.replace('%C%', str(C))
                new_line = new_line.replace('%gamma%', str(gamma))
                new_line = new_line.replace('%segment%', str(segment))
                new_line = new_line.replace('%min_dist%', str(min_max[0]))
                new_line = new_line.replace('%max_dist%', str(min_max[1]))
                new_line = new_line.replace('%num_point%', str(num_point))
                new_line = new_line.replace('%opp_dist%', str(opp_dist))
                new_line = new_line.replace('%date%', str(date_string))
                fout.write(new_line)

def submit_batch():
    os.system('sbatch submit_mod_morphology_script.sh')

for thresh in threshs:
    for snr in snrs:
        for C in Cs:
            for gamma in gammas:
                for segment in segments:
                    for min_max in min_max_dists:
                        for num_point in num_points:
                            for opp_dist in opp_dists:
                                create_submit_script(thresh, snr, C, gamma, segment, min_max, num_point, opp_dist)
                                print(thresh, snr, C, gamma, segment, min_max, num_point, opp_dist)
                                submit_batch()
