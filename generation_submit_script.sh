#!/bin/bash

#SBATCH --job-name=120_30.0_equalize_avg_power_uncorrelated_noise_0_False_generate_recording_ziad2
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=150g
#SBATCH --cpus-per-task=3
#SBATCH --output=SortOutput/generate_recording_ziad_output_equalize_avg_power_120_uncorrelated_noise_0_False_30.0.txt
#SBATCH --time=1-0

python3 ~/SpikeSorting/ziad_mearec_magnetic.py equalize_avg_power 120 30.0 ziad_mearec_templates/mag_templates_flattened_5-25bound_2-4cells_n250_100MEA75.h5 uncorrelated_noise 0 none False
