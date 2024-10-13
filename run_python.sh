#!/bin/bash
#SBATCH --account=rrg-rbond-ac
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --time=23:00:00
#SBATCH --job-name=create_cloudy_directories_and_files
#SBATCH --output=create_cloudy_directories_and_files.out
#SBATCH --error=create_cloudy_directories_and_files.err

cd "/scratch/m/murray/dtolgay/cloudy_runs"

module purge 
ml python/3.11.5

python create_cloudy_directories_and_files.py