import nemo.collections.asr as nemo_asr
from ruamel.yaml import YAML
from omegaconf import DictConfig
import numpy as np
from nemo.collections.asr.models.ctc_models import EncDecCTCModel
from nemo.collections.asr.metrics import wer
import tempfile
import os
import json
import torch

model_to_load = "/TURKISH_FINETUNING_Quartznet15x5_models/epoch=XX-step=XXXXXX.ckpt"
stt_config_path = "/configs/quartznet15x5.yaml"

yaml = YAML(typ='safe')
with open(stt_config_path, encoding="utf-8") as f:
    params = yaml.load(f)

params['model']['train_ds']['manifest_filepath'] = "/data/train_manifest.jsonl"
params['model']['validation_ds']['manifest_filepath'] = "/data/val_manifest.jsonl"

first_asr_model = nemo_asr.models.EncDecCTCModel(cfg=DictConfig(params['model']))
first_asr_model = first_asr_model.load_from_checkpoint(model_to_load)
first_asr_model.eval()


filename = "turkish_fine-tuned_model.onnx"
first_asr_model.export(output=filename)