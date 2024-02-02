
#!pip install soundfile
#!pip install sounddevice
#!pip install pydub
#!pip install numpy

import sys
import soundfile as sf
import sounddevice as sd
from queue import Queue
import time
from pydub import AudioSegment
import numpy as np
import os
#os.remove yerine kullanmak için import ettim os.remove erişim engeli veriyor
import shutil

class Record():

    def __init__(self):
        self.serverSocket = None
        self.queue = Queue()
        self.intensity = 0
        self.GlobalRecord = False


    def setServerSocket(self,serverSocket):
        self.serverSocket = serverSocket

    def createFolder(self,folderName):
        fileCounter = 0
        path = os.getcwd() + "\\" + folderName + str(fileCounter)
        isExist = os.path.exists(path)

        try:
            while isExist:
                fileCounter += 1
                path = os.getcwd() + "\\" + folderName + str(fileCounter)
                isExist = os.path.exists(path)
            os.makedirs(path)
        except Exception as ex:
            print(ex)

        return path


    def startRecord(self,FolderName, FileName, deviceNumber, threshold, timer):
        self.GlobalRecord = True
        recording = False
        name_counter = 1
        print("Kayıt başladı.")

        with sd.InputStream(samplerate=16000, device=deviceNumber, channels=1, callback=self.callback):
            try:
                start_time = time.time()
                path = self.createFolder(FolderName)

                while self.GlobalRecord:
                    if self.intensity > threshold:
                        start_time = time.time()
                        if not recording:
                            file = sf.SoundFile(f"{path}\\{FileName}{name_counter}.wav", mode='x', samplerate=16000,
                                                channels=1, subtype=None)
                            recording = True

                    end_time = time.time()


                    if recording:
                        file.write(self.queue.get())

                    #region kaydı bitir
                    if end_time - start_time > timer and recording:
                        recording = False
                        start_time = end_time
                        file_name = file.name
                        file.close()
                        self.delete_last(file_name, timer)
                        self.serverSocket.write_data(str(file_name))
                        name_counter = name_counter + 1

                    #endregion



                print("Kayıt bitti ve thread sonlandırıldı.")

            except Exception as re:
                print(re)
            except KeyboardInterrupt as k:
                print(k)

    def callback(self,indata, frames, time, status):
        volume_norm = int(np.linalg.norm(indata)*10)
        self.intensity=volume_norm
        self.queue.put(indata.copy())


    def delete_last(self,fileName, time, end_space=0.3):
        if time <= end_space:
            end_space = time - 0.1

        audio = AudioSegment.from_wav(fileName)
        audio = audio[0:-((time - end_space) * 1000)]
        audio.export(fileName, format="wav")

    def stopRecord(self):
        self.GlobalRecord = False

