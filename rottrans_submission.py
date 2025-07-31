import os
from datetime import date

# Fill in these parameters for every run
meas = ['2250000MEA2']
#meas = ['100MEA75']
#cell_ids = ['21', '23', '12', '13']
cell_ids = ['53']
#num_thetas = ['37_0_5', '37_5_10', '37_10_15', '37_15_20', '37_20_25', '37_25_30', '37_30_35', '37_35_37']
#num_thetas = ['37_20_25', '37_5_10']
num_thetas = ['25_0_6', '25_6_12', '25_12_18', '25_18_24']
kvals = [5]
fine_steps = [21]
coarse_steps = [17]
finecoarse_minmaxs = [[-200, 200, -400, 400]]
#fields = [0]
fields = [0, 1]

def create_submit_script(mea, cell_id, num_theta, k, fine_step, coarse_step, fine_min, fine_max, coarse_min, coarse_max, field):
    date_string = str(date.today().month) + '_' + str(date.today().day)
    with open('rottrans_submit_template.sh', 'rt') as fin:
        with open('rottrans_submit_script.sh', 'wt') as fout:
            for line in fin:
                new_line = line.replace('mmm', mea)
                new_line = new_line.replace('iii', str(cell_id))
                new_line = new_line.replace('ttt', str(num_theta))
                new_line = new_line.replace('kkk', str(k))
                new_line = new_line.replace('xxx', str(fine_step))
                new_line = new_line.replace('yyy', str(coarse_step))
                new_line = new_line.replace('qqq', str(fine_min))
                new_line = new_line.replace('www', str(fine_max))
                new_line = new_line.replace('eee', str(coarse_min))
                new_line = new_line.replace('rrr', str(coarse_max))
                new_line = new_line.replace('ddd', str(date_string))
                new_line = new_line.replace('fff', str(field))
                fout.write(new_line)

def submit_batch():
    os.system('sbatch rottrans_submit_script.sh')

for mea in meas:
    for cell_id in cell_ids:
        for num_theta in num_thetas:
            for k in kvals:
                for fine_step in fine_steps:
                    for coarse_step in coarse_steps:
                        for bounds in finecoarse_minmaxs:
                            for field in fields:
                                fine_min, fine_max, coarse_min, coarse_max = bounds
                                create_submit_script(mea, cell_id, num_theta, k, fine_step, coarse_step, fine_min, fine_max, coarse_min, coarse_max, field)
                                submit_batch()














