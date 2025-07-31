#!/bin/bash

#SBATCH --job-name=400MEA50_0_40_1_1.0_default_All_-50_25_25_25_morphology
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=32g
#SBATCH --cpus-per-task=1
#SBATCH --output=MorphologyOutput/morph_output_400MEA50_0_40_1_1.0_default_All_-50_25_25_25_4_3.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/MorphologyModifiedSVM.py 400MEA50 0 40 1 1.0 default All -50 25 25 25
