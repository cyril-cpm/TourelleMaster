from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
from PySimpleGUIDisplay import * 

if __name__ == "__main__":

    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = TKDisplay()

    STR = Settingator(com, display)

    STR.SendInitRequest()

    while display.IsRunning():
           STR.Update()