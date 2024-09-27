#!/bin/bash

python3 vqa_text_unimodal_run.py with \
  seed=3 \
  task_text_unimodal_vqa \
  data_root=./datasets/VQAv2_arrows/ \
  log_dir=./vqa_text_unimodal/ \
  num_gpus=4 \
  per_gpu_batchsize=16 \
  max_epoch=100 \
  learning_rate=1e-4 \
  load_path=./vqa_text_unimodal/best_epoch=57-val/the_metric=0.44.ckpt \
  test_only=True
  #load_path=fiber_pretrain.ckpt \
  #checkpoint_path=./vqa_text_unimodal/last.ckpt