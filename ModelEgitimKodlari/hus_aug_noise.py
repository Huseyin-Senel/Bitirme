import librosa
import json
from os import listdir
from os.path import isfile, join

import torch
import IPython.display as ipd
import os
import soundfile as sf
from nemo.collections.asr.parts.preprocessing import perturb, segment


resampled_path = "content/data/train/wav/" #<------------------------------------------------------------- başına / eklemek yararlı olabilir :)
onlyfiles = [f for f in listdir(resampled_path) if isfile(join(resampled_path, f))]
training_files =[]
for file in onlyfiles:
    training_files.append(file)

#region create manifest
# manifest_path = 'manifest_text.jsonl'
# with open(manifest_path, 'w', encoding="utf-8") as fout:
#     for file in training_files:
#         duration = librosa.core.get_duration(filename=resampled_path+file)
#         metadata = {
#             "audio_filepath": resampled_path+file,
#             "duration": duration,
#             "text": (file.split('.wav')[0]).lower()
#         }
#         json.dump(metadata, fout, ensure_ascii=False)
#         fout.write('\n')
#endregion

#region Change speech pitch

def load_audio(filepath) -> segment.AudioSegment:
    sample_segment = segment.AudioSegment.from_file(filepath, target_sr=sr)
    return sample_segment

sr = 16000
resample_type = 'kaiser_best'

gain = perturb.GainPerturbation(min_gain_dbfs=0, max_gain_dbfs=20)
fast_speed = perturb.SpeedPerturbation(sr, resample_type, min_speed_rate=0.7, max_speed_rate=0.9, num_rates=-1)
tstretch = perturb.TimeStretchPerturbation()


augmentors = []
probas = [1.0 ,0.5]
augmentor = [
    fast_speed,
    gain
]

augmentations = list(zip(probas, augmentor))
fast_augmentor = perturb.AudioAugmentor(augmentations)
augmentors = []

probas = [1.0 ,0.5]
augmentor = [
    tstretch,
    gain
]

augmentations = list(zip(probas, augmentor))
stretch_augmentor = perturb.AudioAugmentor(augmentations)

white_noise = perturb.WhiteNoisePerturbation(min_level=-60, max_level=-55)

resample_type = 'kaiser_best'  # Can be ['kaiser_best', 'kaiser_fast', 'fft', 'scipy']
fast_speed = perturb.SpeedPerturbation(sr, resample_type, min_speed_rate=0.7, max_speed_rate=0.9, num_rates=-1)
slow_speed = perturb.SpeedPerturbation(sr, resample_type, min_speed_rate=1.1, max_speed_rate=1.2, num_rates=-1)

gain = perturb.GainPerturbation(min_gain_dbfs=0, max_gain_dbfs=50)

tstretch = perturb.TimeStretchPerturbation()

##########
WHITE_NOISE_PROB = 0.7
##########

augmentors = []
first_probas = [1.0, 0.7 ,0.5]
first_augmentor = [
    fast_speed,
    white_noise,
    gain
]
augmentations = list(zip(first_probas, first_augmentor))
audio_augmentations = perturb.AudioAugmentor(augmentations)
augmentors.append(audio_augmentations)

###################################

second_probas = [1.0, 0.7 ,0.5]
second_augmentor = [
    slow_speed,
    white_noise,
    gain
]
augmentations = list(zip(second_probas, second_augmentor))
audio_augmentations = perturb.AudioAugmentor(augmentations)
augmentors.append(audio_augmentations)


[augmentor._pipeline for augmentor in augmentors]

#endregion


#region add Noise

def load_audio(filepath) -> segment.AudioSegment:
    sample_segment = segment.AudioSegment.from_file(filepath, target_sr=sr)
    return sample_segment

sr = 16000
aug_funcs = []
noise_manifest_path = "background_noise_16k/noise_manifest.jsonl"

noise = perturb.NoisePerturbation(manifest_path=noise_manifest_path,
                                  min_snr_db=5, max_snr_db=5,
                                  max_gain_db=300.0)
aug_funcs = [noise, noise, noise, noise, noise, noise, noise, noise, noise, noise, noise, noise]

#endregion


#region add manifest file
manifest_path = 'content/data/train_manifest.jsonl' #<----------------------------------------------------------------
with open(manifest_path, 'r') as fin:
    aug_manifest_path = 'train_aug_noise.jsonl'  #<----------------------------------------------------------------
    with open(aug_manifest_path, 'w', encoding="utf-8") as fout:

        for line in fin:
            original_file_json = json.loads(line)
            json.dump(original_file_json, fout, ensure_ascii=False)
            fout.write('\n')

            for i,aug_func in enumerate(aug_funcs):

                sample_segment = load_audio(original_file_json['audio_filepath'])
                aug_func.perturb(sample_segment)

                 # add a new line to the manifest
                new_filepath = f"{original_file_json['audio_filepath'][:-4]}_noise_aug{i}.wav"
                sf.write(new_filepath, sample_segment.samples, sr)

                new_json = original_file_json.copy()
                new_json['audio_filepath'] = new_filepath

                duration = librosa.core.get_duration(filename=new_filepath)
                new_json['duration'] = duration

                json.dump(new_json, fout, ensure_ascii=False)
                fout.write('\n')

#endregion
