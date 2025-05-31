from PySimpleGUIDisplay import *
from Settingator import *
from Player import *
import threading
import gc
import sys

class Players(IRefreshable):
    def __init__(self, settingator:Settingator, strLock:threading.RLock):
        self.__playerList = dict()
        self.__nbPlayers = 0
        self.__orderedPlayerList = dict()
        self.__numberOrderedPlayer = 0

        self.__str:Settingator = settingator
        self.__strLock = strLock

    def AddPlayer(self, slave:Slave):
        print("Adding a player")
        newPlayer = Player(self.__str, self.__strLock)
        print("player created")
        newPlayer.SetSlave(slave)
        newPlayer.Send("GREEN LOADING")
        print("Green loading sended")
        self.__playerList[self.__nbPlayers] = newPlayer
        self.__nbPlayers += 1

    def GetPlayer(self, index:int):
        return self.__playerList[index]
    
    def GetPlayerByOrder(self, orderedIndex:int):
        return self.__orderedPlayerList[orderedIndex]
    
    def GetPlayerBySlaveID(self, slaveID:int):
        for index in self.__playerList:
            if self.__playerList[index].GetSlave().GetID() == slaveID:
                return self.__playerList[index]
        
        return None
    
    def AddOrderedPlayer(self, player:Player):
        if player:
            self.__numberOrderedPlayer += 1
            self.__orderedPlayerList[self.__numberOrderedPlayer] = player
            player.Send("GREEN GOOD")
            player.SetOrder(self.__numberOrderedPlayer)
            player.CreateLayout()
            #display.UpdateLayout(STR.GetSlaveSettings())

    def IsOrderedPlayer(self, slaveID:int) -> bool:
        player = self.GetPlayerBySlaveID(slaveID)

        if player in self.__orderedPlayerList.values():
            return True
        return False

    def GetNumberOfOrderedPlayer(self):
        return self.__numberOrderedPlayer

    def AllAnswered(self):
        allAnswered = True

        for player in self.__playerList:
            if self.__playerList[player].CanAnswer():
                allAnswered = False

        if self.__playerList.__len__() == 0:
            allAnswered = False

        return allAnswered
    
    def ResetAnswered(self):

        for player in self.__playerList:
            self.__playerList[player].ResetAnswered()

    def SendAll(self, command):
        for player in self.__playerList:
            self.__playerList[player].Send(command)

    def GetList(self):
        return self.__playerList
    
    def SetAllBGColor(self, color):

        for player in self.__playerList:
            self.__playerList[player].SetFrameBGColor(color)

    def ReWriteName(self):

        for player in self.__playerList:
            self.__playerList[player].ReWriteName()

    def ReWritePosition(self):

        for player in self.__playerList:
            self.__playerList[player].ReWritePosition()

    def ResetScore(self):
        for player in self.__playerList:
            self.__playerList[player].ResetScore()

    def UpdateAllScore(self):
        for player in self.__playerList:
            self.__playerList[player].UpdateScore()

    def RefreshElementDisplay(self) -> None:
        self.UpdateAllScore()
        self.ReWriteName()
        self.ReWritePosition()

    def ResetPlayer(self) -> None:

        for player in self.__playerList:
            self.__playerList[player].Send("GREEN LOADING")

        self.__orderedPlayerList.clear()
        self.__nbPlayers = 0
        self.__playerList.clear()
        gc.collect()

