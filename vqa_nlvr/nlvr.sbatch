#!/bin/bash
#SBATCH --nodes=1                        # requests 1 compute server
#SBATCH --ntasks-per-node=1              # runs 1 tasks on each server
#SBATCH --cpus-per-task=4                # uses 4 compute cores per task
#SBATCH --gres=gpu:rtx8000:4
#SBATCH --time=48:00:00
#SBATCH --mem=128GB
#SBATCH --job-name=nlvr
#SBATCH --output=nlvr.out
#SBATCH --error=nlvr-error.txt
#SBATCH --mail-user=matthew.dong@nyu.edu
#SBATCH --mail-type=FAIL

singularity exec --nv --overlay $SCRATCH/new_env/overlay-50G-10M.ext3:ro /scratch/work/public/singularity/cuda11.8.86-cudnn8.7-devel-ubuntu22.04.2.sif /bin/bash -c "
source /ext3/miniconda3/etc/profile.d/conda.sh
conda activate
conda activate multimodal_env
pwd
env_list=$(conda env list)
echo "$env_list"
nvidia-smi
WANDB_API_KEY = "01a7f15f8823bf8acd4bf2863f0e3fd89e05b212"
export WANDB_API_KEY
echo $WANDB_API_KEY | wandb login --relogin
./test.sh
"
