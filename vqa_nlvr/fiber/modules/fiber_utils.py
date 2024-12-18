import torch
import random

from transformers.optimization import AdamW
from transformers import (
    get_polynomial_decay_schedule_with_warmup,
    get_cosine_schedule_with_warmup,
)
from .dist_utils import all_gather
from ..gadgets.my_metrics import Accuracy, VQAScore, Scalar


def set_metrics(pl_module):
    for split in ["train", "val"]:
        for k, v in pl_module.hparams.config["loss_names"].items():
            if v <= 0:
                continue
            if k == "vqa":
                setattr(pl_module, f"{split}_vqa_score", VQAScore())
                setattr(pl_module, f"{split}_{k}_loss", Scalar())
            elif k == "nlvr2":
                setattr(pl_module, f"{split}_{k}_accuracy", Accuracy())
                setattr(pl_module, f"{split}_{k}_loss", Scalar())
            elif k == "itm":
                setattr(pl_module, f"{split}_{k}_accuracy", Accuracy())
                setattr(pl_module, f"{split}_{k}_loss", Scalar())
            elif k == "itc":
                setattr(pl_module, f"{split}_{k}_i2t_accuracy", Accuracy())
                setattr(pl_module, f"{split}_{k}_t2i_accuracy", Accuracy())
                setattr(pl_module, f"{split}_{k}_loss", Scalar())
                setattr(pl_module, f"{split}_{k}_logit_scale", Scalar())
            else:
                setattr(pl_module, f"{split}_{k}_accuracy", Accuracy())
                setattr(pl_module, f"{split}_{k}_loss", Scalar())


def epoch_wrapup(pl_module):
    phase = "train" if pl_module.training else "val"
    the_metric = 0
    debug = pl_module.hparams.config["loss_names"].items()
    print(f"Items in PL Module: {debug}")
    for loss_name, v in pl_module.hparams.config["loss_names"].items():
        if v <= 0:
            continue

        value = 0
        print(f"Loss Name:{loss_name}")
        if loss_name == "vqa":
            value = getattr(pl_module, f"{phase}_{loss_name}_score").compute()
            pl_module.log(f"{loss_name}/{phase}/score_epoch", value)
            getattr(pl_module, f"{phase}_{loss_name}_score").reset()
            pl_module.log(
                f"{loss_name}/{phase}/loss_epoch",
                getattr(pl_module, f"{phase}_{loss_name}_loss").compute(),
            )
            getattr(pl_module, f"{phase}_{loss_name}_loss").reset()
        elif loss_name == "nlvr2":
            # if phase == "train":
                value = getattr(pl_module, f"{phase}_{loss_name}_accuracy").compute()
                print(f"Value: {value}")
                pl_module.log(f"{loss_name}/{phase}/accuracy_epoch", value)
                getattr(pl_module, f"{phase}_{loss_name}_accuracy").reset()
                pl_module.log(
                    f"{loss_name}/{phase}/loss_epoch",
                    getattr(pl_module, f"{phase}_{loss_name}_loss").compute(),
                )
                getattr(pl_module, f"{phase}_{loss_name}_loss").reset()
        the_metric += value

    pl_module.log(f"{phase}/the_metric", the_metric)


def check_non_acc_grad(pl_module):
    if pl_module.token_type_embeddings.weight.grad is None:
        return True
    else:
        grad = pl_module.token_type_embeddings.weight.grad
        return (grad.sum() == 0).item()


def set_task(pl_module):
    pl_module.current_tasks = [k for k, v in pl_module.hparams.config["loss_names"].items() if v > 0]
    return


def set_schedule(pl_module):
    lr = pl_module.hparams.config["learning_rate"]
    wd = pl_module.hparams.config["weight_decay"]

    no_decay = [
        "bias",
        "LayerNorm.bias",
        "LayerNorm.weight",
        "norm.bias",
        "norm.weight",
        "norm1.bias",
        "norm1.weight",
        "norm2.bias",
        "norm2.weight",
    ]
    head_names = ["vqa_classifier", "nlvr2_classifier", "mlm_score", "itm_score", "snli_classifier"]
    cross_modal_names = ["cross_modal", "i2t", "t2i"]
    lr_mult_head = pl_module.hparams.config["lr_mult_head"]
    lr_mult_cross_modal = pl_module.hparams.config["lr_mult_cross_modal"]
    end_lr = pl_module.hparams.config["end_lr"]
    decay_power = pl_module.hparams.config["decay_power"]
    optim_type = pl_module.hparams.config["optim_type"]

    total_list = [n for n, p in pl_module.named_parameters()]
    list_1 = [n for n, p in pl_module.named_parameters()
                if not any(nd in n for nd in no_decay)
                and not any(bb in n for bb in head_names)
                and not any(ht in n for ht in cross_modal_names)
            ]
    print(list(set(total_list) - set(list_1)))
    # for n, p in pl_module.named_parameters():
        
    optimizer_grouped_parameters = [
        {
            ### All parameters not a part of any of the lists
            "params": [
                p
                for n, p in pl_module.named_parameters()
                if not any(nd in n for nd in no_decay)
                and not any(bb in n for bb in head_names)
                and not any(ht in n for ht in cross_modal_names)
            ],
            "weight_decay": wd,
            "lr": lr,
        },
        ## All paramrameters that dont require a decay
        {
            "params": [
                p
                for n, p in pl_module.named_parameters()
                if any(nd in n for nd in no_decay)
                and not any(bb in n for bb in head_names)
                and not any(ht in n for ht in cross_modal_names)
            ],
            "weight_decay": 0.0,
            "lr": lr,
        },
        ## VQA classifier
        {
            "params": [
                p
                for n, p in pl_module.named_parameters()
                if not any(nd in n for nd in no_decay)
                and any(bb in n for bb in head_names)
                and not any(ht in n for ht in cross_modal_names)
            ],
            "weight_decay": wd,
            "lr": lr * lr_mult_head,
        },
        ## VQA classifier with no decay
        {
            "params": [
                p
                for n, p in pl_module.named_parameters()
                if any(nd in n for nd in no_decay)
                and any(bb in n for bb in head_names)
                and not any(ht in n for ht in cross_modal_names)
            ],
            "weight_decay": 0.0,
            "lr": lr * lr_mult_head,
        },
         ## Cross modal weights and not a part of no decay
        {
            "params": [
                p
                for n, p in pl_module.named_parameters()
                if not any(nd in n for nd in no_decay)
                and not any(bb in n for bb in head_names)
                and any(ht in n for ht in cross_modal_names)
            ],
            "weight_decay": wd,
            "lr": lr * lr_mult_cross_modal,
        },
        ## Cross modal weights and part of no decay
        {
            "params": [
                p
                for n, p in pl_module.named_parameters()
                if any(nd in n for nd in no_decay)
                and not any(bb in n for bb in head_names)
                and any(ht in n for ht in cross_modal_names)
            ],
            "weight_decay": 0.0,
            "lr": lr * lr_mult_cross_modal,
        },
    ]

    if optim_type == "adamw":
        optimizer = AdamW(optimizer_grouped_parameters, lr=lr, eps=1e-8, betas=(0.9, 0.98))
    elif optim_type == "adam":
        optimizer = torch.optim.Adam(optimizer_grouped_parameters, lr=lr)
    elif optim_type == "sgd":
        optimizer = torch.optim.SGD(optimizer_grouped_parameters, lr=lr, momentum=0.9)

    if pl_module.trainer.max_steps is None:
        max_steps = (
            len(pl_module.trainer.datamodule.train_dataloader())
            * pl_module.trainer.max_epochs
            // pl_module.trainer.accumulate_grad_batches
        )
    else:
        max_steps = pl_module.trainer.max_steps

    warmup_steps = pl_module.hparams.config["warmup_steps"]
    if isinstance(pl_module.hparams.config["warmup_steps"], float):
        warmup_steps = int(max_steps * warmup_steps)

    if decay_power == "cosine":
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=max_steps,
        )
    else:
        scheduler = get_polynomial_decay_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=max_steps,
            lr_end=end_lr,
            power=decay_power,
        )

    sched = {"scheduler": scheduler, "interval": "step"}

    return (
        [optimizer],
        [sched],
    )