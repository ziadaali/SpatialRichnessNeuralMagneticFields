#!/bin/bash

#SBATCH --job-name=200_100MEA75_SomaFlattened-equalize_avg_power_Bursting-False_uncorrelated_noise_2_120_30.0_Half2_ziad_spike_sorting
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --constraint GPU_CC:8.9
#SBATCH --mem=64g
#SBATCH --cpus-per-task=4
#SBATCH --output=SortOutput/sort_output_200_100MEA75_SomaFlattened-equalize_avg_power_Bursting-False_uncorrelated_noise_2_120_30.0_Half2_3_1.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/ziad_spikesorting.py 200 100MEA75_SomaFlattened-equalize_avg_power_Bursting-False_uncorrelated_noise 2 120 30.0 Half2
