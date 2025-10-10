from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
from PySimpleGUIDisplay import * 
import time
import pygame.mixer as mx
import random


BUZZ_BUTTON = 5

buzzed = True
buzzedTeam = 0
buzzedSlave = None

def delay():
    time.sleep(0.05)

def ReInit(value):
    STR.BridgeReInitSlaves()

btReInit = LayoutElement(IDP_BUTTON, None, "reinitSlave", callback=ReInit)

def reloadAll(value):
    slaves = STR.GetSlaves()

    for id in slaves:
        slaves[id].SendInitRequest(id)

reloadButton = LayoutElement(IDP_BUTTON, None, "reload", callback=reloadAll)

def sendInitRequestFunc(value):
    STR.SendInitRequest()

sendInitRequestButton = LayoutElement(IDP_BUTTON, None, "SendInitRequest", callback=sendInitRequestFunc)

def startBridgeInitFunc(value):
    STR.BridgeStartInitBroadcasted(initModule)

def stopBridgeInitFunc(value):
    STR.BridgeStopInitBroadcasted()


startBridgeInitButton = LayoutElement(IDP_BUTTON, None, "StartBridgeInit", callback=startBridgeInitFunc)
stopBridgeInitButton = LayoutElement(IDP_BUTTON, None, "StopBridgeInit", callback=stopBridgeInitFunc)

def displayLayout(value):
    if int(value):
        STR.DisplaySlaveLayout()
    else:
        STR.RemoveSlaveLayout()

layoutDisplayCheck = LayoutElement(IDP_CHECK, None, "DisplayLayout", callback=displayLayout)

def openingCallback(value):
    module = STR.GetSlaveWithSetting("LEDMODULE")

    module.SendSettingUpdateByName("0BaseTransi_RATE_BEGIN", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_END", 255)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TIME", 2500)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TRANSITION")
    delay()

openingButton = LayoutElement(IDP_BUTTON, None, "Opening", callback=openingCallback)


def preOpeningCallback(value):
    module = STR.GetSlaveWithSetting("LEDMODULE")

    module.SendSettingUpdateByName("5SimonWin_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("5SimonWin_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_BEGIN", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_DIRECTION", 3)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("5SimonWin_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TRANSITION")
    delay()

preOpeningButton = LayoutElement(IDP_BUTTON, None, "PreOpening", callback=preOpeningCallback)

def idleCallback(value):
    module = STR.GetSlaveWithSetting("LEDMODULE")

    module.SendSettingUpdateByName("5SimonWin_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("5SimonWin_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("5SimonWin_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_TRANSITION")
    delay()

    module.SendSettingUpdateByName("0BaseTransi_RATE_BEGIN", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_END", 255)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TIME", 1)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TRANSITION")
    delay()

idleButton = LayoutElement(IDP_BUTTON, None, "Idle", callback=idleCallback)

blinkShouldRespond = False

def randomCallback(value):
    global blinkShouldRespond
    module = STR.GetSlaveWithSetting("LEDMODULE")

    module.SendSettingUpdateByName("3Reset1Transi_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_END", 255)
    delay()
    module.SendSettingUpdateByName("5SimonWin_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("5SimonWin_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_TIME", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_END", 0)
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TIME", 0)
    delay()

    module.SendSettingUpdateByName("4BlinkTransi_RATE_TIME", 10000)
    delay()
    module.SendSettingUpdateByName("4BlinkTransi_RATE_END", 127)
    delay()
    module.SendSettingUpdateByName("4BlinkTransi_RATE_BEGIN", 0)
    delay()
    module.SendSettingUpdateByName("4BlinkTransi_RATE_MIDSPEED", 200)
    delay()

    module.SendSettingUpdateByName("5SimonWin_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("6SimonLoose_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("0BaseTransi_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("3Reset1Transi_RATE_TRANSITION")
    delay()
    module.SendSettingUpdateByName("4BlinkTransi_RATE_TRANSITION")
    delay()
    blinkShouldRespond = True

randomButton = LayoutElement(IDP_BUTTON, None, "random", callback=randomCallback)

def endBlinkTransi(slave:int):
    global blinkShouldRespond
    if blinkShouldRespond:
        module = STR.GetSlaveWithSetting("LEDMODULE")

        newVal = 0
        if random.choice([True, False]):
            newVal = 255
        
        module.SendSettingUpdateByName("4BlinkTransi_RATE_TIME", 5000)
        delay()
        module.SendSettingUpdateByName("4BlinkTransi_RATE_END", newVal)
        delay()
        module.SendSettingUpdateByName("4BlinkTransi_RATE_BEGIN", 127)
        delay()
        module.SendSettingUpdateByName("4BlinkTransi_RATE_TRANSITION")
        blinkShouldRespond = False


mancheMitraille = False

buzzerTeamList = []
buzzerSlaveList = []
buzzerTimestamp = dict()

def activateMancheMitrailleCallback(value):
    global mancheMitraille
    mancheMitraille = True

    for slave in buzzerSlaveList:
        if slave.GetSettingByName("TEAM").GetValue() < 3:
            slave.SendSettingUpdateByName("RED", 0)
            delay()
            slave.SendSettingUpdateByName("GREEN", 0)
            delay()
            slave.SendSettingUpdateByName("BLUE", 255)
            delay()
        else:
            slave.SendSettingUpdateByName("RED", 255)
            delay()
            slave.SendSettingUpdateByName("GREEN", 0)
            delay()
            slave.SendSettingUpdateByName("BLUE", 0)
            delay()

    for slave in buzzerSlaveList:
        slave.SendSettingUpdateByName("UPDATE_LED")
        delay()

mancheMitrailleOnButton = LayoutElement(IDP_BUTTON, None, "Manche Mitraille ON", callback=activateMancheMitrailleCallback)

def stopMancheMitrailleCallback(value):
    global mancheMitraille
    mancheMitraille = False

    for slave in buzzerSlaveList:
        slave.SendSettingUpdateByName("RED", 0)
        delay()
        slave.SendSettingUpdateByName("GREEN", 0)
        delay()
        slave.SendSettingUpdateByName("BLUE", 0)
        delay()
        
    for slave in buzzerSlaveList:
        slave.SendSettingUpdateByName("UPDATE_LED")
        delay()

mancheMitrailleOffButton = LayoutElement(IDP_BUTTON, None, "Manche Mitraille OFF", callback=stopMancheMitrailleCallback)

simonActivated = False

simonSequence = []

def launchMatch(level):
    global simonSequence

    simonSequence = []
    for i in range(0, level+4):
        simonSequence.append(random.choice([True, False]))

def endDisplay():
    pass

def initSimon(value):
    global simonActivated
    simonActivated = True

    module = STR.GetSlaveWithSetting("LEDMODULE")

    if module != None:
        module.SendSettingUpdateByName("SetBaseFadeing")

    launchMatch(1)

startSimonButton = LayoutElement(IDP_BUTTON, None, "Start Simon", callback=initSimon)

def initModule(slave):
    if slave.GetSettingByName("TEAM") != None:
        global buzzerTeamList
        global buzzerSlaveList

        team = slave.GetSettingByName("TEAM").GetValue()

        if team not in buzzerTeamList:
            buzzerTeamList.append(team)
            buzzerSlaveList.append(slave)

        if team not in buzzerTimestamp:
            buzzerTimestamp[team] = 0

        slave.SendSettingUpdateByName("RED", 0)
        delay()
        slave.SendSettingUpdateByName("GREEN", 0)
        delay()
        slave.SendSettingUpdateByName("BLUE", 0)
        delay()
        slave.SendSettingUpdateByName("UPDATE_LED")
        delay()

def buzzButton(slaveID:int):
    buzzSlave = STR.GetSlave(slaveID)
    if buzzSlave != None:
        teamSetting = buzzSlave.GetSettingByName("TEAM")

        if teamSetting != None:
            teamValue = teamSetting.GetValue()

            if teamValue not in buzzerTimestamp:
                buzzerTimestamp[teamValue] = 0

            if time.time() - buzzerTimestamp[teamValue] > 1:
                buzzerTimestamp[teamValue] = time.time()

                if mancheMitraille:
                    if teamValue < 3:
                        buble = STR.GetSlaveWithSetting("TRIG0")
                        if buble != None:
                            buble.SendSettingUpdateByName("TRIG0")
                    else:
                        rifle = STR.GetSlaveWithSetting("SHOOT")
                        if rifle != None:
                            rifle.SendSettingUpdateByName("SHOOT")
        

if __name__ == "__main__":

    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = TKDisplay()

    STR = Settingator(com, display)

    STR.AddToLayout(openingButton)
    STR.AddToLayout(preOpeningButton)
    STR.AddToLayout(idleButton)
    STR.AddToLayout(randomButton)
    STR.AddToLayout(mancheMitrailleOnButton)
    STR.AddToLayout(mancheMitrailleOffButton)
    STR.AddToLayout(startSimonButton)

    STR.AddNotifCallback(BUZZ_BUTTON, buzzButton)
    STR.AddNotifCallback(52, endBlinkTransi)

    STR.AddToLayout(reloadButton)

    STR.AddToLayout(startBridgeInitButton)
    STR.AddToLayout(stopBridgeInitButton)

    STR.AddToLayout(sendInitRequestButton)

    STR.AddToLayout(btReInit)

    STR.AddToLayout(layoutDisplayCheck)

    STR.BridgeStartInitBroadcasted(initModule)

    while display.IsRunning():
        STR.Update()