#!/bin/bash

#SBATCH --job-name=400MEA75_0.005_0_10_1.0_default_Eighth5_morphology
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=16g
#SBATCH --cpus-per-task=1
#SBATCH --output=MorphologyOutput/morph_output_400MEA75_0.005_0_10_1.0_default_Eighth5_1_25.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/MorphologyReconstruction.py 400MEA75 0.005 0 10 1.0 default Eighth5
