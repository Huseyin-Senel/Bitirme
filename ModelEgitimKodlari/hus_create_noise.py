import os
import soundfile as sf
import torchaudio
import librosa
import json
from os import listdir
from os.path import isfile, join


dataset_dir = 'background_noise'
resampled_path = 'background_noise_16k/'
manifest_path = 'background_noise_16k/noise_manifest.jsonl'


#region Resample background noise
original_files = []

recordings = [os.path.join(dataset_dir, name) for name in os.listdir(dataset_dir) if
              os.path.isfile(os.path.join(dataset_dir, name))]

for file in recordings:
    original_files.append(file)

for file in original_files:
    y, sr = torchaudio.load(file)
    y = y.mean(dim=0)  # if there are multiple channels, average them to single channel
    resampler = torchaudio.transforms.Resample(sr, 16000)
    y_resampled = resampler(y)
    new_path = os.path.join(resampled_path, file.split("/")[-1])
    sf.write(new_path, y_resampled.numpy(), 16000)
#endregion


#region Create noise manifest
onlyfiles = [f for f in listdir(resampled_path) if isfile(join(resampled_path, f))]
training_files =[]
for file in onlyfiles:
    training_files.append(file)


with open(manifest_path, 'w', encoding="utf-8") as fout:
    for file in training_files:
        duration = librosa.core.get_duration(filename=resampled_path+file)
        metadata = {
            "audio_filepath": resampled_path+file,
            "duration": duration,
            "label": "noise",
            "text": "_",
            "offset": 0.0
        }
        json.dump(metadata, fout, ensure_ascii=False)
        fout.write('\n')
#endregion