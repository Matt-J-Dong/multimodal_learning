#!/bin/bash

python3 run.py with \
  seed=3 \
  task_text_unimodal_nlvr2 \
  data_root=./datasets/NLVR2_arrows/ \
  log_dir=./nlvr_text_unimodal/ \
  num_gpus=1 \
  per_gpu_batchsize=16 \
  max_epoch=100 \
  learning_rate=1e-4 \
  load_path=fiber_pretrain.ckpt \
  #checkpoint_path=./nlvr_text_unimodal/last.ckpt