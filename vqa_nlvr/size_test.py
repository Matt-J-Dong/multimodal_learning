import torch

# Load the pre-trained checkpoint
pretrained_ckpt = torch.load('./fiber_pretrain.ckpt')

# Load the latest best epoch checkpoint
latest_best_ckpt = torch.load('./vqa_inter_modality/best_epoch=16-val/the_metric=0.64.ckpt')

# Compare keys in state_dicts
pretrained_keys = set(pretrained_ckpt['state_dict'].keys())
latest_best_keys = set(latest_best_ckpt['state_dict'].keys())

missing_keys = pretrained_keys - latest_best_keys
extra_keys = latest_best_keys - pretrained_keys

print("Missing keys in latest best checkpoint:", missing_keys)
print("Extra keys in latest best checkpoint:", extra_keys)
