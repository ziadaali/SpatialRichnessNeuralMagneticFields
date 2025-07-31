import os
from datetime import date

# Fill in these parameters for every run
durations = [20, 60, 120]
noises = [5.0, 15.0, 30.0]
noise_modes = ['equalize_avg_power']
#noise_modes = ['equalize_peak_power']
#far_noise = 'ziad-far-neurons'
far_noise = 'uncorrelated_noise'
far_neurons = '0'
bursting_setting = 'False'

template_file = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n250_100MEA75.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n300_Neuropixels-128.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_0-6cells_n300_100MEA75.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_cells2-3_radius36.0_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_cells2-3_radius100.0_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_cells2-3_radius10-25_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'mag_templates_flattened_cells2-3_radius100.0_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_n400_cells2-3_radius25-50_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_n400_cells2-3_radius50-75_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_n400_cells2-3_radius75-100_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_cells2-3_n200_no-axon_100MEA75.h5'
#template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_cells2-3_radius100.0_zlim_-535.5_535.5_Neuropixels-128_no_axon.h5'
#template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n250_100MEA75.h5'

noise_template_file = 'none'
#noise_template_file = f'/home/groups/adapoon/ziad/SpikeSorting/ziad_mearec_templates/mag_templates_flattened_noise_n500_cells2-3_radius100-200_zlim_-535.5_535.5_Neuropixels-128.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_5bound_10-25rot_2-4cells_n300_Neuropixels-128_3.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n250_100MEA50.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n300_100MEA100.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_2-4cells_zlim35_n300_100MEA75zlim35.h5'
#template_file = f'ziad_mearec_templates/mag_templates_flattened_2-4cells_zlim285_n300_100MEA75zlim285.h5'

#template_file = f'ziad_mearec_templates/mag_templates_flattened_2cells_delta_100MEA75.h5'

deltas = [2, 4, 6, 8, 10, 15]
#deltas = [25, 50, 75, 100, 125, 150]
#deltas = [125, 150]

code = 'ziad_mearec_magnetic.py'
if 'delta' in template_file:
    code = 'ziad_mearec_2cells.py'

def create_submit_script(noise_mode, duration, noise, template_file):
    #date_string = str(date.today().month) + '_' + str(date.today().day)
    with open('generation_submit_template.sh', 'rt') as fin:
        with open('generation_submit_script.sh', 'wt') as fout:
            for line in fin:
                new_line = line.replace('ppp', noise_mode)
                new_line = new_line.replace('ddd', str(duration))
                new_line = new_line.replace('nnn', str(noise))
                new_line = new_line.replace('ttt', template_file)
                new_line = new_line.replace('xxx', code)
                if 'magnetic' in code:
                    new_line = new_line.replace('fff', '')
                else:
                    new_line = new_line.replace('fff', str(delta))
                new_line = new_line.replace('qqq', far_noise)
                new_line = new_line.replace('www', far_neurons)
                new_line = new_line.replace('eee', noise_template_file)
                new_line = new_line.replace('rrr', bursting_setting)
                fout.write(new_line)

def submit_batch():
    os.system('sbatch generation_submit_script.sh')

for noise_mode in noise_modes:
    for duration in durations:
        for noise in noises:
            if 'delta' in template_file:
                for delta in deltas:
                    print(noise_mode, duration, noise, delta)
                    temp_file = template_file.replace('delta', str(delta) + 'delta')
                    create_submit_script(noise_mode, duration, noise, temp_file)
                    submit_batch()
            else:
                print(noise_mode, duration, noise)
                create_submit_script(noise_mode, duration, noise, template_file)
                submit_batch()
