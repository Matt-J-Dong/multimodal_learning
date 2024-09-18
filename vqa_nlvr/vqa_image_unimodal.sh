#!/bin/bash

python3 vqa_image_unimodal_run.py with \
  seed=3 \
  task_image_unimodal_vqa \
  data_root=./datasets/VQAv2_arrows/ \
  log_dir=./vqa_image_unimodal/ \
  num_gpus=4 \
  per_gpu_batchsize=16 \
  max_epoch=100 \
  learning_rate=1e-4 \
  load_path=fiber_pretrain.ckpt \
  test_only = True
  #load_path=fiber_pretrain.ckpt \
  #checkpoint_path=./vqa_image_unimodal/last.ckpt