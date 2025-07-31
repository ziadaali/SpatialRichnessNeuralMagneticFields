#!/bin/bash

#SBATCH --job-name=%mea%_%thresh%_%snr%_%iters%_%C%_%gamma%_%segment%_%min_dist%_%max_dist%_%num_point%_%opp_dist%_morphology
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-cpu=32g
#SBATCH --cpus-per-task=1
#SBATCH --output=MorphologyOutput/morph_output_%mea%_%thresh%_%snr%_%iters%_%C%_%gamma%_%segment%_%min_dist%_%max_dist%_%num_point%_%opp_dist%_%date%.txt
#SBATCH --time=2-0

python3 ~/SpikeSorting/MorphologyModifiedSVM.py %mea% %thresh% %snr% %iters% %C% %gamma% %segment% %min_dist% %max_dist% %num_point% %opp_dist%
