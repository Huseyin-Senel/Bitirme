from tkinter import *
import tkinter.font as font
import threading
import pyaudio

import sumo
from sumo import Sumo


class Window():

    def __init__(self, record):
        self.word_dict_TR = ['ileri git', 'sağa dön', 'sola dön', 'geri git', 'sağa git']

        self.sumo = None
        self.record = record
        # window
        self.win = Tk()
        self.win.geometry("1280x720")
        self.win.wm_title("Application Interface")
        self.win.minsize(1280, 720)
        self.win.iconbitmap(default="voice.ico")

        # frame_top
        self.frame_t = Frame(self.win, bg="#add8e6")
        self.frame_t.place(relx=0.0250, rely=0.05, relwidth=0.95, relheight=0.1)

        # header
        self.header = Label(self.frame_t, text="ROBOTIC VEHICLE CONTROLLED BY USING VOICE", font="Times 18 bold",
                            bg="#add8e6")
        self.header.place(relx=0.01, rely=0.01, relwidth=1, relheight=1)

        # frame_middle
        self.frame_m = Frame(self.win, bg="#add8e6")
        self.frame_m.place(relx=0.0250, rely=0.14, relwidth=0.95, relheight=0.55)

        # textBox
        Label(self.frame_m, text="Results of Voice Model", font="Times 19", bg="#add8e6").pack(padx=10, pady=5,
                                                                                               anchor="s")

        self.resultsTextBox1 = Text(self.frame_m, background="white", font="Calibri 18", bg="white", cursor="arrow")
        self.resultsTextBox1.place(relx=0.02, rely=0.1, relwidth=0.3, relheight=0.8)
        self.resultsTextBox1.config(state=DISABLED)

        self.resultsTextBox2 = Text(self.frame_m, background="white", font="Calibri 18", bg="white", cursor="arrow")
        self.resultsTextBox2.place(relx=0.34, rely=0.1, relwidth=0.32, relheight=0.8)
        self.resultsTextBox2.config(state=DISABLED)

        # scrollBar
        self.scrollBar1 = Scrollbar(self.resultsTextBox1, orient='vertical')
        self.scrollBar1.pack(side=RIGHT, fill='y')
        self.scrollBar1.config(command=self.resultsTextBox1.yview)
        self.scrollBar1.bind("<Configure>")

        self.scrollBar2 = Scrollbar(self.resultsTextBox2, orient='vertical')
        self.scrollBar2.pack(side=RIGHT, fill='y')
        self.scrollBar2.config(command=self.resultsTextBox2.yview)
        self.scrollBar2.bind("<Configure>")

        # frame_middle spinbox
        current_value = StringVar(value=7)
        self.spinboxDecibel = Spinbox(self.frame_m, from_=0, to=100, textvariable=current_value, font="Times 22")
        self.spinboxDecibel.place(relx=0.877, rely=0.40, relwidth=0.1, relheight=0.1)
        Label(self.frame_m, text=f"Decibel Threshold", font="Times 18", background="#add8e6").place(relx=0.68,
                                                                                                    rely=0.42)

        # Sumo
        # self.frame_Sumo = Frame(self.frame_m, bg="white")
        # self.frame_Sumo.place(relx=0.68, rely=0.1, relwidth=0.3, relheight=0.8)

        # frame_bottom
        self.frame_b = Frame(self.win, bg="#add8e6")
        self.frame_b.place(relx=0.0250, rely=0.705, relwidth=0.95, relheight=0.2)

        # buttons
        # self.startButton = Button(self.frame_b, text="Start Recording", font="Times 22", command=self.startFunction, bg="#33ff69")
        self.startButton = Button(self.frame_b, text="Start Recording", font="Times 22", command=self.startFunction,
                                  bg="#618069", state="disabled", disabledforeground="black")
        self.stopButton = Button(self.frame_b, text="Stop Recording", font="Times 22", command=self.stopFunction,
                                 bg="#806162", state="disabled", disabledforeground="black")
        self.clearButton = Button(self.frame_b, text="Clear Results", font="Times 22", command=self.clearFunction,
                                  bg="white")

        self.startButton.place(relx=0.02, rely=0.2, relwidth=0.3, relheight=0.6)
        self.stopButton.place(relx=0.34, rely=0.2, relwidth=0.32, relheight=0.6)
        self.clearButton.place(relx=0.68, rely=0.2, relwidth=0.3, relheight=0.6)

        # choose_audio_device button

        audio = pyaudio.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        numDevices = info.get('deviceCount')
        self.deviceList = []

        # !!!!!!! burada range 1 den başlattım, 0 lı haline bakabilirsin
        for i in range(0, numDevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                self.deviceList.append(audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        self.value_inside = StringVar(self.frame_b)
        self.value_inside.set("Choose Input Device")

        deviceOptionMenu = OptionMenu(self.frame_m, self.value_inside, *self.deviceList)
        deviceOptionMenu.config(font=('Times', 16))

        menu = self.win.nametowidget(deviceOptionMenu.menuname)
        menu.config(font=('Times', 16))

        deviceOptionMenu.place(relx=0.68, rely=0.25, relwidth=0.3, relheight=0.1)


        # modelStateButton
        self.modelStatusLabel = Label(self.frame_m, text="Model Loading ...", font="Times 22", bg="#add8e6")
        self.modelStatusLabel.place(relx=0.68, rely=0.1)

        self.modelStateButton = Button(self.frame_m, bg="red")
        # Label(frame_m, text=f"{modelStateButtonText()}", font="Times 22", background="#add8e6").place(relx=0.68,rely=0.1)
        self.modelStateButton.place(relx=0.936, rely=0.116, relwidth=0.04, relheight=0.08)
        self.modelStateButton["state"] = "disabled"

    def startFunction(self, folderName="Records\RecordFolder", fileName="RecordAudio",
                      thresholdTime=0.4):
        if (self.value_inside.get() == "Choose Input Device"):
            self.insertRow("Lütfen giriş aygıtı seçiniz", "Please choose input device")
            return

        self.startButton.config(state="disabled", bg='#618069', disabledforeground="black")
        self.stopButton.config(state="normal", bg="#ff3333")

        def recordThread():
            #print("threshold",self.spinboxDecibel.get())
            #print("device",self.value_inside.get(),self.deviceList.index(self.value_inside.get()))
            self.record.startRecord(folderName, fileName, self.deviceList.index(self.value_inside.get()), int(self.spinboxDecibel.get()), thresholdTime)

        rt1 = threading.Thread(target=recordThread)
        rt1.start()

    def stopFunction(self):
        self.stopButton.config(state="disabled", bg="#806162", disabledforeground="black")
        self.startButton.config(state="normal", bg="#33ff69")

        self.resultsTextBox1.config(state="normal")
        self.resultsTextBox1.config(state="disabled")

        self.record.stopRecord()

    def clearFunction(self):
        self.resultsTextBox1.config(state="normal")
        self.resultsTextBox1.delete('1.0', 'end')
        self.resultsTextBox1.config(state="disabled")

        self.resultsTextBox2.config(state="normal")
        self.resultsTextBox2.delete('1.0', 'end')
        self.resultsTextBox2.config(state="disabled")

        self.startButton.config(state="normal", bg="#33ff69")
        self.stopButton.config(state="disabled", bg="#806162", disabledforeground="black")

    # def insertRow(self,text1, text2,is_data=True):
    #     if not is_data:
    #         self.cmdTextBox1.config(state="normal")
    #         self.cmdTextBox1.insert(END, f"{text1} - {text2}\n")
    #         self.cmdTextBox1.see("end")
    #         self.cmdTextBox1.config(state="disabled")
    #     else:
    #         self.resultsTextBox1.config(state="normal")
    #         self.resultsTextBox1.insert(END, f"{text1}\n")
    #         self.resultsTextBox1.see("end")
    #         self.resultsTextBox1.config(state="disabled")
    #
    #         self.resultsTextBox2.config(state="normal")
    #         self.resultsTextBox2.insert(END, f"{text2}\n")
    #         self.resultsTextBox2.see("end")
    #         self.resultsTextBox2.config(state="disabled")

    def insertRow(self, text1, text2):
        self.resultsTextBox1.config(state="normal")
        self.resultsTextBox1.insert(END, f"{text1}\n")
        self.resultsTextBox1.see("end")
        self.resultsTextBox1.config(state="disabled")

        self.resultsTextBox2.config(state="normal")
        self.resultsTextBox2.insert(END, f"{text2}\n")
        self.resultsTextBox2.see("end")
        self.resultsTextBox2.config(state="disabled")

        # with self.sumo.lock:
        # self.sumo.set_route_by_instruction(self.linuxLangToSumoLang(text1))
        self.sumo.instruction = self.linuxLangToSumoLang(text1)
        self.sumo.runInstruction = True

    def modelLoaded(self):
        self.modelStatusLabel.config(text="Model Loaded")
        self.modelStateButton.config(bg="green")
        self.startButton.config(state="normal", bg="#33ff69")
        self.createSumo()

    def startWindow(self):
        self.win.mainloop()

    def linuxLangToSumoLang(self, instruction):
        if instruction == self.word_dict_TR[0]:
            return sumo.instruction_forward
        elif instruction == self.word_dict_TR[1]:
            return sumo.instruction_right
        elif instruction == self.word_dict_TR[2]:
            return sumo.instruction_left
        elif instruction == self.word_dict_TR[3]:
            return sumo.instruction_backward
        elif instruction == self.word_dict_TR[4]:
            return sumo.instruction_right
        else:
            return ""

# region Sumo
    def createSumo(self):
        def startSumo():
            self.sumo = Sumo(self)
            self.sumo.run()

        self.t3 = threading.Thread(target=startSumo)
        self.t3.start()

    def stop(self):
        self.sumo.stop = True
        self.t3.join()
        print("Sumo sonlandırıldı ...")
# endregion