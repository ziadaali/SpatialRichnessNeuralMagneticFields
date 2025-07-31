#!/bin/bash

#SBATCH --job-name=ddd_nnn_pppfff_qqq_www_rrr_generate_recording_ziad2
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=150g
#SBATCH --cpus-per-task=3
#SBATCH --output=SortOutput/generate_recording_ziad_output_ppp_ddd_qqq_www_rrr_nnnfff.txt
#SBATCH --time=1-0

python3 ~/SpikeSorting/xxx ppp ddd nnn ttt qqq www eee rrr
