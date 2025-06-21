from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
from PySimpleGUIDisplay import * 

def startBroadcast(value):
    STR.BridgeStartInitBroadcasted(lambda slaveID: print(slaveID))

if __name__ == "__main__":

    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = TKDisplay()

    STR = Settingator(com, display)

    bt = LayoutElement(IDP_BUTTON, None, "broadcast", callback=startBroadcast)

    STR.AddToLayout(bt)

    while display.IsRunning():
        STR.Update()