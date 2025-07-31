#!/bin/bash

#SBATCH --job-name=matlab_test1
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=20g
#SBATCH --cpus-per-task=1
#SBATCH --output=matlab_test1_output.txt
#SBATCH --time=1-0

matlab -nodesktop -nodisplay -nosplash -r "run('matlab_test.m');exit;"
