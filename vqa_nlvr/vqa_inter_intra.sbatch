#!/bin/bash
#SBATCH --nodes=1                        # requests 1 compute server
#SBATCH --ntasks-per-node=1              # runs 1 tasks on each server
#SBATCH --cpus-per-task=4                # uses 4 compute cores per task
#SBATCH --gres=gpu:4
#SBATCH --time=48:00:00
#SBATCH --mem=128GB
#SBATCH --job-name=vqa_inter_intra
#SBATCH --output=vqa_inter_intra.out
#SBATCH --error=vqa_inter_intra-error.txt
#SBATCH --mail-user=matthew.dong@nyu.edu
#SBATCH --mail-type=ALL

singularity exec --nv --overlay $SCRATCH/new_env/overlay-50G-10M.ext3:ro /scratch/work/public/singularity/cuda11.8.86-cudnn8.7-devel-ubuntu22.04.2.sif /bin/bash -c "
source /ext3/miniconda3/etc/profile.d/conda.sh
conda activate multimodal_env

# Verify environment
pwd
env_list=\$(conda env list)
echo "\$env_list"

# Check GPU status
nvidia-smi

# Source .env if it exists
if [ -f .env ]; then
    source .env
fi

# Set and export WANDB API key
export WANDB_API_KEY=\$WANDB_API_KEY
wandb login --relogin \$WANDB_API_KEY

# Run your script
./vqa_inter_intra.sh
"