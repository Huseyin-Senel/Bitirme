#!pip install wget
#!apt-get install sox libsndfile1 ffmpeg
#!pip install text-unidecode
#!pip install matplotlib>=3.3.2

#!pip install Cython
## Install NeMo
#BRANCH = 'main'
#!python -m pip install git+https://github.com/NVIDIA/NeMo.git@$BRANCH#egg=nemo_toolkit[all]
#!apt-get update && apt-get install -y libsndfile1 ffmpeg
#!pip install tensorflow==2.11.0 Pygments==2.6.1 pynini==2.1.5 nemo_toolkit[all]
import sys
import threading
from client import Client

import nemo.collections.asr as nemo_asr
import Levenshtein


model_path = 'epoch=99-step=44280.ckpt' #/home/huseyin/bitirme/

ip = sys.argv[1]

dataSeparator = ","

word_dict_TR = ['ileri git', 'sağa dön', 'sola dön', 'geri git', 'sağa git','simülasyon']
word_dict_EN = ['go forward', 'turn right', 'turn left', 'go back', 'go right','simulation']

#region Socket Client Setup

threadLock = threading.Lock()


def client_data_readed(self):
    if self.data:
        print("Serverden mesaj alındı: " + str(self.data))

        if self.socketDataTypes[0] in self.data:
            command = self.decoder(self.data)
            if command == self.socketCommands[3]:
                stop()

        elif self.socketDataTypes[1] in self.data:
            data = self.decoder(self.data)
            threadLock.acquire()
            predict(data)
            threadLock.release()

Client.data_readed = client_data_readed
cl = None
def thread2():
    global cl
    cl = Client(ip)
t2 = threading.Thread(target=thread2)
t2.start()
#endregion


model = nemo_asr.models.EncDecCTCModel.from_pretrained("QuartzNet15x5Base-En")
model1 = model.load_from_checkpoint(model_path)
model1.eval()
cl.write_data(cl.socketCommands[0])

print("Model dinlemeye basladi ...")


def predict(folderPath):
    #adres = folderPath.decode('windows-1252')
    adres = "/mnt/" + folderPath
    adres = adres.replace("\\", "/").replace("C:", "c").replace('\r', '').replace('\n', '')
    # print(adres)
    predictModel(adres)

def correct(string1):
    string1 = string1[0]
    global word_dict_TR, word_dict_EN

    sel_index = -1
    min = float('inf')
    for index, string in enumerate(word_dict_TR):
        sayi = Levenshtein.distance(string1, string)
        if (sayi < min):
            min = sayi
            sel_index = index

    if (len(string1) - ((len(string1) / 100) * 40) < min):

        string1 = string1.replace(" ", "")
        new_dict = [x.replace(" ", "") for x in word_dict_TR]

        sel_index = -1
        min = float('inf')
        for index, string in enumerate(word_dict_TR):
            sayi = Levenshtein.distance(string1, string)
            if (sayi < min):
                min = sayi
                sel_index = index

        if (len(string1) - ((len(string1) / 100) * 60) < min):
            print("! eşleşme bulunmadı,! no match found")
            cl.write_data("! eşleşme bulunmadı,! no match found")
        else:
            print(word_dict_TR[sel_index]+","+word_dict_EN[sel_index])
            cl.write_data(str(word_dict_TR[sel_index]+","+word_dict_EN[sel_index]))
    else:
        print(word_dict_TR[sel_index]+","+word_dict_EN[sel_index])
        cl.write_data(str(word_dict_TR[sel_index]+","+word_dict_EN[sel_index]))

def predictModel(audio_path):
    # audio_path='/mnt/c/Users/Psycr/OneDrive/Masaüstü/RaporBitirme/SoundCutterCode/RecordFolder2/RecordAudio1.wav'

    sonuc = model1.transcribe([audio_path])
    # print(sonuc)
    correct(sonuc)

def stop():
    global cancelationToken
    cancelationToken = True
    global cl
    cl.stop()
    t2.join()
    print("Model dinlemeyi durdurdu ve sonlandırıldı ...")

