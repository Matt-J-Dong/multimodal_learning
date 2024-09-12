#!/bin/bash

python3 run.py with \
  seed=3 \
  task_inter_and_intra_multimodal_nlvr2 \
  data_root=./datasets/NLVR2_arrows/ \
  log_dir=./inter_and_intra_modality/ \
  num_gpus=4 \
  per_gpu_batchsize=8 \
  max_epoch=100 \
  learning_rate=1e-4 \
  load_path=fiber_pretrain.ckpt
