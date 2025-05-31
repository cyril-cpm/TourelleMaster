from Settingator import *
from PySerialCommunicator import *
import random
import time
import multiprocessing
import sys
import gc
from TKDisplay import *
from PySimpleGUIDisplay import * 
from QuestionAndScoreDisplay import *

from Players import *
from Game import *

import threading



com:SerialCTR

display:TKDisplay

QADisplay:QuestionAndScoreDisplay

STR:Settingator = None

###   GAME SYSTEM    ###

NUMBER_PLAYER = 3
TESTING = False

turret:Slave


game:Game          
        
########################


### TARGETING SYSTEM ###


LASER_DETECTED = 2
LASER_NOTIF = 0x05


def targetPlayer(orderedPlayer:int):
    target.TargetPlayer(orderedPlayer)

def notifLaser(slaveID:int):

    global step
    global target_side
    global targetting
    global turretPos
    global targetedPlayer
    global targetDone
    global targetDoneTimestamp

    if targetting and slaveID == targetedPlayer.GetSlave().GetID():
        print("targetedPlayer is " + str(targetedPlayer.GetOrder()))
        if step == 0:
            turret.SendSettingUpdateByName("SPEED", 128)

            if target_side == "R":
                turret.SendSettingUpdateByName("GAUCHE")
            elif target_side == "L":
                turret.SendSettingUpdateByName("DROITE")
            step = 3

        elif step == 3:
            turret.SendSettingUpdateByName("SPEED", 64)

            if target_side == "R":
                turret.SendSettingUpdateByName("DROITE")
            elif target_side == "L":
                turret.SendSettingUpdateByName("GAUCHE")
            step = 4

        elif step == 4:
            step = 0
            target_side = ""
            targetting = False

            targetedPlayer.GetSlave().RemoveDirectSettingUpdateConfig(turret, LASER_DETECTED)
            targetedPlayer = None
            targetDone = True
            targetDoneTimestamp = time.time()
        
        display.UpdateSetting(turret.GetSettingByName("SPEED"))

    print("Laser Detected")
    print(slaveID)
    turretPos = playerList.GetPlayerBySlaveID(slaveID).GetOrder()

########################

###   INIT SYSTEM    ###

def startGameAuto(game):
    game.Start(AUTO)


def startGameManual(wvalue):
    game.Start(MANUAL)

startGameManualButton = LayoutElement(IDP_BUTTON, None, "startGameManual", callback=startGameManual)

def initPlayer(value):
    STR.AddNotifCallback(RED_BUTTON, initNotifLaser)

InitPlayerButton = LayoutElement(IDP_BUTTON, None, "initPlayer", callback=initPlayer)

def startBroadcast(value):
    STR.BridgeStartInitBroadcasted()

StartBroadcastButton = LayoutElement(IDP_BUTTON, None, "start broadcast", callback=startBroadcast)

def startBroadcastTurret(value):
    STR.BridgeStartInitBroadcasted(lambda slave : TURRET.Init(slave))

StartBroadcastTurretButton = LayoutElement(IDP_BUTTON, None, "broadcast Turret", callback=startBroadcastTurret)

def startBroadcastDesk(value):
    STR.BridgeStartInitBroadcasted(DeskCallback)

StartBroadcastDeskButton = LayoutElement(IDP_BUTTON, None, "broadcast Desk", callback=startBroadcastDesk)

def stopBroadcast(value):
    STR.BridgeStopInitBroadcasted()

StopBroadcastButton = LayoutElement(IDP_BUTTON, None, "stop broadcast", callback=stopBroadcast)

def nouvelleManche(value):
    global game
    game.Handling()

NouvelleMancheButton = LayoutElement(IDP_BUTTON, None, "Nouvelle Manche", callback=nouvelleManche)

#TEST#

def testDisplayQuestion(value):
    game.SetQuestionDisplay("Combien de fois par seconde un colibri peut-il battre des ailes ?", "La réponse A", "La grosse réponse B", "repC", "Et non pas la D")

testDisplayQuestionButton = LayoutElement(IDP_BUTTON, None, "testDisplayQuestion", callback=testDisplayQuestion)

def testDisplayScore(value):
    game.TestScoreAnnounce()

testDisplayScoreButton = LayoutElement(IDP_BUTTON, None, "testDisplayScore", callback=testDisplayScore)

######

def initNotifLaser(slaveID:int):
    playerList = game.GetPlayerList()
    if playerList.IsOrderedPlayer(slaveID):
        return
    playerList.AddOrderedPlayer(playerList.GetPlayerBySlaveID(slaveID))

    if playerList.GetNumberOfOrderedPlayer() >= NUMBER_PLAYER:
        STR.RemoveNotifCallback(RED_BUTTON)

        display.UpdateLayout()

        STR.AddNotifCallback(RED_BUTTON, lambda slaveID : game.playerPressButton(slaveID, RED_BUTTON))
        STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : game.playerPressButton(slaveID, GREEN_BUTTON))
        STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : game.playerPressButton(slaveID, BLUE_BUTTON))
        STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : game.playerPressButton(slaveID, YELLOW_BUTTON))

########################


########################

def DeskCallback(slave:Slave):
    game.AddPlayer(slave)

def TurretCallback(slave:Slave):
    game.SetTurret(slave)

####### TESTING ########

def CreateDummyPlayers(game:Game):
    game.AddPlayer(Slave(STR, 0, dict()))
    game.AddOrderedPlayer(game.GetPlayer(0))
    game.GetPlayer(0).SetScore(0, 3)

    game.AddPlayer(Slave(STR, 1, dict()))
    game.AddOrderedPlayer(game.GetPlayer(1))
    game.GetPlayer(1).SetScore(2, 1)

    game.AddPlayer(Slave(STR, 2, dict()))
    game.AddOrderedPlayer(game.GetPlayer(2))
    game.GetPlayer(2).SetScore(3, 0)

    game.AddPlayer(Slave(STR, 3, dict()))
    game.AddOrderedPlayer(game.GetPlayer(3))
    game.GetPlayer(3).SetScore(1, 2)

def testButtonColor(game):
    game.playerPressButton(0, RED_BUTTON)
    game.playerPressButton(1, GREEN_BUTTON)
    game.playerPressButton(2, BLUE_BUTTON)
    game.playerPressButton(3, YELLOW_BUTTON)
    display.Update()

########################

def CheckPlayer(value):
    print("CheckPlayer")
    for obj in gc.get_objects():
            if isinstance(obj, Player):
                print(sys.getrefcount(obj) - 2)
                refs = gc.get_referrers(obj)
                for ref in refs:
                    if isinstance(obj, WeakMethod):
                        print("WeakRefMethod")
                    else:
                        print(type(ref), ref)
                        print("")

def GameThreadFunction(STR:Settingator, lock:threading.RLock):
   
    global game
    game = Game(STR, lock)

    game.SetQADisplay(QADisplay)

    ControlColumnLayout = LayoutElement(IDP_COLUMN)

    
    ControlColumnLayout.AppendElement(StartBroadcastTurretButton)
    ControlColumnLayout.AppendElement(StartBroadcastDeskButton)
    ControlColumnLayout.AppendElement(StopBroadcastButton)

    ControlColumnLayout.AppendElement(InitPlayerButton)

    startGameAutoButton = LayoutElement(IDP_BUTTON, None, "startGameAuto", callback=lambda value : startGameAuto(game))
    ControlColumnLayout.AppendElement(startGameAutoButton)

    ControlColumnLayout.AppendElement(NouvelleMancheButton)

    if TESTING:
        ControlColumnLayout.AppendElement(startGameAutoButton)
        ControlColumnLayout.AppendElement(startGameManualButton)
        pass

    ControlColumnLayout.AppendElement(testDisplayQuestionButton)
    ControlColumnLayout.AppendElement(testDisplayScoreButton)

    if TESTING:
        ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "test button Color", callback=lambda value : testButtonColor(game)))

    ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "Reset Score", callback=lambda value : game.ResetScore()))

    ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "Reset Player", callback=lambda value : game.ResetPlayer()))

    ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "Check Player", callback=CheckPlayer))

    with lock:
        STR.AddToLayout(ControlColumnLayout)
        #STR.SendInitRequest(1, lambda slave : TURRET.Init(slave))
        #STR.SendBridgeInitRequest(1, b'Turret', lambda slave : TURRET.Init(slave))
        #STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)

    

    if TESTING:
        CreateDummyPlayers(game)

    game.run()

if __name__ == "__main__":

    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = TKDisplay()

    STR = Settingator(com, display)
    STR.AddNotifCallback(RED_BUTTON, lambda slaveID : game.playerPressButton(slaveID, RED_BUTTON))
    STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : game.playerPressButton(slaveID, GREEN_BUTTON))
    STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : game.playerPressButton(slaveID, BLUE_BUTTON))
    STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : game.playerPressButton(slaveID, YELLOW_BUTTON))

    STR.AddNotifCallback(LASER_NOTIF, notifLaser)

    STR.Update()

    QADisplay = QuestionAndScoreDisplay()

    STRLock = threading.RLock()

    GameThread = threading.Thread(target=GameThreadFunction, args=(STR, STRLock),name="GameThread")

    GameThread.start()

    while display.IsRunning():
        QADisplay.run()
        with STRLock:
            STR.Update()

    GameThread.join()
