#!/bin/bash

#SBATCH --job-name=60_ziad_spike_sorting
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=1
#SBATCH --output=sort_output_60.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/ziad_spikesorting.py 60
