import os
from datetime import date
from ziad_functions_submission import generate_field_list

# Fill in these parameters for every run
mea_name = '400MEA75'

#threshs = [0, 0.001, 0.005]
threshs = [0.005]

snrs = [0]
#snrs = [0]

iters_per_cell = 10
Cs = [1.0]
gammas = ['default']

#segments = ['Quarter1', 'Quarter2', 'Quarter3', 'Quarter4']
#segments = ['Eighth1', 'Eighth2', 'Eighth3', 'Eighth4', 'Eighth5', 'Eighth6', 'Eighth7', 'Eighth8']
#segments = ['Eighth1', 'Eighth2', 'Eighth3', 'Eighth4']
#segments = ['Eighth2', 'Eighth4', 'Eighth6', 'Eighth7', 'Eighth8']
segments = ['Eighth5']
#segments = ['Quarter1']

def create_submit_script(thresh, snr, C, gamma, segment):
    date_string = str(date.today().month) + '_' + str(date.today().day)
    with open('submit_morphology_template.sh', 'rt') as fin:
        with open('submit_morphology_script.sh', 'wt') as fout:
            for line in fin:
                new_line = line.replace('%mea%', str(mea_name))
                new_line = new_line.replace('%thresh%', str(thresh))
                new_line = new_line.replace('%snr%', str(snr))
                new_line = new_line.replace('%iters%', str(iters_per_cell))
                new_line = new_line.replace('%C%', str(C))
                new_line = new_line.replace('%gamma%', str(gamma))
                new_line = new_line.replace('%segment%', str(segment))
                new_line = new_line.replace('%date%', str(date_string))
                fout.write(new_line)

def submit_batch():
    os.system('sbatch submit_morphology_script.sh')

for thresh in threshs:
    for snr in snrs:
        for C in Cs:
            for gamma in gammas:
                for segment in segments:
                    create_submit_script(thresh, snr, C, gamma, segment)
                    print(thresh, snr, C, gamma, segment)
                    submit_batch()
