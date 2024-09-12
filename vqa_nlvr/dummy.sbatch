#!/bin/bash
#SBATCH --nodes=1                        # requests 1 compute server
#SBATCH --ntasks-per-node=1              # runs 1 tasks on each server
#SBATCH --cpus-per-task=1                # uses 4 compute cores per task
#SBATCH --time=1:00:00
#SBATCH --mem=4GB
#SBATCH --job-name=dummy-test
#SBATCH --output=dummy.out

pwd
ls -l