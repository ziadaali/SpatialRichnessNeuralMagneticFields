#!/bin/bash

#SBATCH --job-name=2250000MEA2_53_25_18_24_5_21_17_-200_200_-400_400_1_ziad_rottrans
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=128g
#SBATCH --cpus-per-task=1
#SBATCH --output=/home/groups/adapoon/ziad/SpikeSorting/CorrelationOutput/corr_output_2250000MEA2_53_25_18_24_5_21_17_-200_200_-400_400_1_5_29.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/ZIAD_MEARotation2.py 2250000MEA2 53 25_18_24 5 21 17 -200 200 -400 400 1
