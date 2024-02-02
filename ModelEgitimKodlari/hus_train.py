import nemo.collections.asr as nemo_asr
from ruamel.yaml import YAML
import pytorch_lightning as pl
from omegaconf import DictConfig, OmegaConf, open_dict
import copy
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks import ModelCheckpoint
import os


def training_quartznet():
    EPOCHS = 100

    config_path = "configs/config.yaml"

    yaml = YAML(typ='safe')
    with open(config_path) as f:
        params = yaml.load(f)

    params['model']['train_ds']['manifest_filepath'] = "content/data/train_manifest.jsonl"
    params['model']['validation_ds']['manifest_filepath'] = "content/data/val_manifest.jsonl"

    first_asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained("QuartzNet15x5Base-En")

    first_asr_model.change_vocabulary(
        new_vocabulary=[" ", "a", "b", "c", "ç", "d", "e", "f", "g", "ğ", "h", "ı", "i", "j", "k", "l", "m",
                        "n", "o", "ö", "p", "q", "r", "s", "ş", "t", "u", "ü", "v", "w", "x", "y", "z", "'"])

    new_opt = copy.deepcopy(params['model']['optim'])

    new_opt['lr'] = 0.001
    # Point to the data we'll use for fine-tuning as the training set
    first_asr_model.setup_training_data(train_data_config=params['model']['train_ds'])
    # Point to the new validation data for fine-tuning
    first_asr_model.setup_validation_data(val_data_config=params['model']['validation_ds'])
    # assign optimizer config
    first_asr_model.setup_optimization(optim_config=DictConfig(new_opt))

    wandb_logger = WandbLogger(name="Quartznet15x5", project="TURKISH_LEARNING_2")
    # used for saving models
    save_path = os.path.join(os.getcwd(), "TURKISH_LEARNING_2" + "_" + "Quartznet15x5_models")
    checkpoint_callback = ModelCheckpoint(
        dirpath=save_path,
        save_top_k=-1,
        verbose=True,
        monitor='val_loss',
        mode='min',
    )

    trainer = pl.Trainer(accelerator='cpu',
                         max_epochs=EPOCHS,
                         logger=wandb_logger, log_every_n_steps=1,
                         val_check_interval=1.0, enable_checkpointing=checkpoint_callback)

    first_asr_model.set_trainer(trainer)

    trainer.fit(first_asr_model)


if __name__ == '__main__':
    training_quartznet()