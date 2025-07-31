#!/bin/bash

#SBATCH --job-name=%%%_!!!_qqq_ttt_nnn_hhh_ziad_spike_sorting
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --constraint GPU_CC:8.9
#SBATCH --mem=64g
#SBATCH --cpus-per-task=4
#SBATCH --output=SortOutput/sort_output_%%%_!!!_qqq_ttt_nnn_hhh_ddd.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/ziad_spikesorting.py %%% !!! qqq ttt nnn hhh
