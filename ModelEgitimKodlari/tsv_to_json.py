import sys
import argparse
import csv
import json
import logging
import multiprocessing
import os
import tarfile
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List

import sox
from sox import Transformer
import wget
from tqdm import tqdm



parser = argparse.ArgumentParser(description='tsv files convert json')
parser.add_argument("--data_root", default='dataset/', type=str, help="Directory to store the dataset.")
parser.add_argument('--manifest_dir', default='./', type=str, help='Output directory for manifests')
parser.add_argument("--num_workers", default=multiprocessing.cpu_count(), type=int, help="Workers to process dataset.")
parser.add_argument('--sample_rate', default=16000, type=int, help='Sample rate')
parser.add_argument('--files_to_process', nargs='+', default=['test.tsv','dev.tsv', 'train.tsv'],
                    type=str, help='list of *.csv file names to process')#

# parser.add_argument('--version', default='cv-corpus-11.0-2022-09-21',
#                     type=str, help='Version of the dataset (obtainable via https://commonvoice.mozilla.org/en/datasets')

parser.add_argument('--language', default='tr',
                    type=str, help='dil kodu')

# args = parser.parse_args()
args, unknown = parser.parse_known_args()




def create_manifest(
        data: List[tuple],
        output_name: str,
        manifest_path: str):
    output_file = Path(manifest_path) / output_name
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with output_file.open(mode='w', encoding="utf-8") as f:
        for wav_path, duration, text in tqdm(data, total=len(data)):
            f.write(
                json.dumps({
                    'audio_filepath': wav_path,
                    "duration": duration,
                    'text': text
                },  ensure_ascii=False) + '\n'
            )

def process_files(csv_file, data_root, num_workers):
    wav_dir = os.path.join(data_root, 'wav/')
    os.makedirs(wav_dir, exist_ok=True)
    audio_clips_path = os.path.dirname(csv_file) + '/clips/'

    def process(x):
        file_path, text = x
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        text = text.lower().strip()
        audio_path = os.path.join(audio_clips_path, file_path)
        output_wav_path = os.path.join(wav_dir, file_name + '.wav')

        tfm = Transformer()
        tfm.rate(samplerate=args.sample_rate)
        tfm.build(
            input_filepath=audio_path,
            output_filepath=output_wav_path
        )
        duration = sox.file_info.duration(output_wav_path)
        return output_wav_path, duration, text

    logging.info('Converting mp3 to wav for {}.'.format(csv_file))
    with open(csv_file, encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        next(reader, None)  # skip the headers
        data = [(row['path'], row['sentence']) for row in reader]
        print(data)
        with ThreadPool(num_workers) as pool:
            data = list(tqdm(pool.imap(process, data), total=len(data)))

    print(data)

    return data


def main():
    data_root = args.data_root
    os.makedirs(data_root, exist_ok=True)
    folder_path = os.path.join(data_root,args.language)

    for csv_file in args.files_to_process:
        data = process_files(
            csv_file=os.path.join(folder_path, csv_file),
            data_root=os.path.join(data_root, os.path.splitext(csv_file)[0]),
            num_workers=args.num_workers
        )
        logging.info('Creating manifests...')
        create_manifest(
            data=data,
            output_name=f'commonvoice_{os.path.splitext(csv_file)[0]}_manifest.jsonl',
            manifest_path=args.manifest_dir,
        )



if __name__ == "__main__":
    main()