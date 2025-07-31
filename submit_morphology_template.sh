#!/bin/bash

#SBATCH --job-name=%mea%_%thresh%_%snr%_%iters%_%C%_%gamma%_%segment%_morphology
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=16g
#SBATCH --cpus-per-task=1
#SBATCH --output=MorphologyOutput/morph_output_%mea%_%thresh%_%snr%_%iters%_%C%_%gamma%_%segment%_%date%.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/MorphologyReconstruction.py %mea% %thresh% %snr% %iters% %C% %gamma% %segment%
