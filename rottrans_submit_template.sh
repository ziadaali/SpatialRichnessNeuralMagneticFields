#!/bin/bash

#SBATCH --job-name=mmm_iii_ttt_kkk_xxx_yyy_qqq_www_eee_rrr_fff_ziad_rottrans
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=128g
#SBATCH --cpus-per-task=1
#SBATCH --output=/home/groups/adapoon/ziad/SpikeSorting/CorrelationOutput/corr_output_mmm_iii_ttt_kkk_xxx_yyy_qqq_www_eee_rrr_fff_ddd.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/ZIAD_MEARotation2.py mmm iii ttt kkk xxx yyy qqq www eee rrr fff
