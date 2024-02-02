import subprocess
import threading

from record import Record
from server import Server
from ui import Window



subprocessText = ['wsl', '/usr/bin/python3', 'linuxMain.py'] #/home/huseyin/bitirme/
dataSeparator = ","


#region Socket Server Setup
def server_data_readed(self):

    #global socketCommands,ss1
    if self.data:
        print("Message received from client: " + str(self.data))

        if self.socketDataTypes[0] in self.data: #command
            command = self.decoder(self.data)
            if command == self.socketCommands[0]:
                app.modelLoaded()
            elif command == self.socketCommands[1]:
                app.record.setServerSocket(ss1)

        elif self.socketDataTypes[1] in self.data: #data
            data = self.decoder(self.data)
            data_array = str(data).split(dataSeparator)
            app.insertRow(data_array[0], data_array[1])
            #app.sumo.set_route_by_instruction(app.linuxLangToSumoLang(data_array[0]))


Server.data_read = server_data_readed
ss1 = None

def startServer():
    global ss1
    ss1 = Server()
    ss1.start()
t1 = threading.Thread(target=startServer)
t1.start()
#endregion

app = Window(Record())

subprocessText.append(ss1.host)
#region Run LinuxMain.py
def startModel():
    subprocess.call(subprocessText)
t2 = threading.Thread(target=startModel)
t2.start()
#endregion

app.startWindow()



#region Stop App
print("-------------------CLOSING-----------------------")
app.stop()

ss1.write_data(ss1.socketCommands[3])
t2.join()

ss1.stop()
t1.join()

print("Application terminated...")
print("-------------------------------------------------")
#endregion