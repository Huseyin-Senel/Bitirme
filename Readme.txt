Programın çalışabilmesi için Winowsta WSL kurulu olması gerekmektedir (bkz. https://learn.microsoft.com/en-us/windows/wsl/install)

WSL üzerinde python3 kurulu olmalı ve içerisinde şu modüller bulunmalıdır.(komutlar)

sudo apt-get update
sudo apt-get install sox libsndfile1 ffmpeg
sudo python -m pip install --upgrade pip
sudo pip install matplotlib>=3.3.2
sudo pip install Cython
sudo pip install wget
sudo pip install text-unidecode
sudo python -m pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[all]
sudo pip install tensorflow==2.11.0 
sudo pip install Pygments==2.6.1 
sudo pip install pynini==2.1.5 
sudo pip install nemo_toolkit[all]
sudo pip install Levenshtein


Windows üzerinde SUMO ve Python3.8(veya üzeri) yüklü olması gerekmektedir. (bkz. https://eclipse.dev/sumo/)
SUMO PATH'i mutlaka sistem ortam değişkenlerine eklenmelidir.

windows üzerindeki pythonda şu modüller bulunmalıdır.
traci (kullanılan sürüm 1.15.0) 
sumolib (kullanılan sürüm 1.15.0) 
soundfile (kullanılan sürüm 0.10.3.post1)
sounddevice (kullanılan sürüm 0.4.6) 
pydub (kullanılan sürüm 0.25.1) 
numpy (kullanılan sürüm 1.22.4)
tk (kullanılan sürüm 8.6.12)



Gerekli özellikler kurulduktan sonra Windows ortamındaki python üzerinde main.py dosyasını çalıştırınız.