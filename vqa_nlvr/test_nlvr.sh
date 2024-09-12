#!/bin/bash

python3 run.py with \
  seed=3 \
  task_inter_modality_nlvr2 \
  data_root=./datasets/VQAv2_arrows/ \
  log_dir=./inter_and_intra_modality/ \
  num_gpus=4 \
  per_gpu_batchsize=16 \
  max_epoch=100 \
  learning_rate=1e-4 \
  load_path=fiber_pretrain.ckpt
