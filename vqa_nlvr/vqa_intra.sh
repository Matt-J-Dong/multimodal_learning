#!/bin/bash

python3 vqa_intra_run.py with \
  seed=3 \
  task_intra_modality_vqa \
  data_root=./datasets/VQAv2_arrows/ \
  log_dir=./vqa_intra_modality/ \
  num_gpus=4 \
  per_gpu_batchsize=16 \
  max_epoch=100 \
  learning_rate=1e-4 \
  load_path=fiber_pretrain.ckpt #\
  #test_only=True
  #load_path=./vqa_inter_modality/best_epoch=16-val/the_metric=0.64.ckpt
  #checkpoint_path=./vqa_inter_modality/best_epoch=16-val/the_metric=0.64.ckpt
  
  
  
