from Display import *
from Settingator import *
import threading
from Sound import *
from Target import *
from weakref import WeakMethod
import gc
import sys

class Player():
    def __init__(self, settingator:Settingator, strLock:threading.RLock):
        self.__score = 0
        self.__good = 0
        self.__bonus = 0
        self.__bad = 0
        self.__slave = None
        self.__order = 0
        self.__answeredCurrentQuestion = False
        self.__lastAnswer = None
        self.__name = "non défini"
        self.__position = 5.0
        self.__positionElement:LayoutElement = None
        self.__goodElement:LayoutElement = None
        self.__badElement:LayoutElement = None
        self.__playerLayout:LayoutElement = None

        self.__str:Settingator = settingator
        self.__strLock = strLock

        self.__playerLock:threading.RLock = threading.RLock()

    def __del__(self):
        with self.__strLock:
            self.__str.RemoveFromLayout(self.__playerLayout)

    def CreateLayout(self) -> None:
        frameName:str = "Player " + str(self.__order) + " : Slave " + str(self.GetSlave().GetID())

        weakSetPosition = WeakMethod(self.SetPosition)
        weakGetPosition = WeakMethod(self.GetPosition)
        weakSetName = WeakMethod(self.SetName)

        self.__positionElement = LayoutElement(IDP_INPUT, self.GetPosition(), "Target Position", callback=lambda value : weakSetPosition() and weakSetPosition()(value))
        self.__goodElement = LayoutElement(IDP_TEXT, "Good: " + str(self.__good))
        self.__badElement = LayoutElement(IDP_TEXT, "Bad: " + str(self.__bad))

        self.__playerLayout = LayoutElement(IDP_COLUMN, None, frameName, [
                                                        LayoutElement(IDP_BUTTON, None, "target", callback=lambda value : TURRET.MoveToPosition(weakGetPosition()() if weakGetPosition() is not None else None)),
                                                        LayoutElement(IDP_TEXT, "Player Name"),
                                                        LayoutElement(IDP_INPUT, self.GetName(), "Player Name", callback=lambda value : weakSetName() and weakSetName()(value)),
                                                        LayoutElement(IDP_TEXT, "Target Position :"),
                                                        self.__positionElement,
                                                        self.__goodElement,
                                                        self.__badElement
                                                    ])
        
        with self.__strLock:
            self.__str.AddToLayout(self.__playerLayout)

    def GetName(self):
        return self.__name
    
    def SetName(self, name):
        with self.__playerLock:
            self.__name = name

    def GetPosition(self) -> float:
        return self.__position
    
    def SetPosition(self, position):
        if position == '':
            position = 0

        with self.__playerLock:
            self.__position = float(position)

    def SetSlave(self, slave:Slave):
        with self.__playerLock:
            self.__slave = slave

    def Send(self, settingName:str):
        if isinstance(self.__slave, Slave):
            self.__slave.SendSettingUpdateByName(settingName)

    def GetSlave(self):
        return self.__slave

    def GetOrder(self):
        return self.__order
    
    def SetOrder(self, order:int):
        with self.__playerLock:
            self.__order = order

    def CanAnswer(self):
        return not self.__answeredCurrentQuestion
    
    def ResetAnswered(self):
        with self.__playerLock:
            self.SetAnswered(False)
            self.__lastAnswer = None

    def SetAnswered(self, value:bool = True):
        with self.__playerLock:
            self.__answeredCurrentQuestion = value

    def SetLastAnswer(self, value:int):
        with self.__playerLock:
            self.__lastAnswer = value
            self.SetAnswered()

    def GetLastAnswer(self):
        return self.__lastAnswer
    
    def IncreaseGood(self):
        with self.__playerLock:
            self.__good += 1
            self.UpdateScore()
    
    def IncreaseFail(self):
        with self.__playerLock:
            self.__bad += 1
            self.UpdateScore()

    def ResetScore(self):
        self.SetScore(0, 0)

    def UpdateScore(self):
        with self.__playerLock:
            self.__score = self.__good - self.__bad

        if self.__goodElement != None:
            self.__goodElement.UpdateValue("Good: " + str(self.__good))

        if self.__badElement != None:
            self.__badElement.UpdateValue("Bad: " + str(self.__bad))

    def GetScore(self):
        return self.__score
    
    def GetGood(self):
        return self.__good
    
    def GetBad(self):
        return self.__bad
    
    def SetScore(self, good, bad):
        with self.__playerLock:
            self.__good = good
            self.__bad = bad
        self.UpdateScore()

    def GetFrameElement(self):
        return self.__frameElement
    
    def SetFrameBGColor(self, color):
        self.__playerLayout.GetIElement().SetBGColor(color)
    
    def ReWriteName(self):
        if (self.__nameElement()):
            self.__nameElement.GetValue().UpdateValue(self.__name)

    def ReWritePosition(self):
        if (self.__positionElement()):
            self.__positionElement.GetValue().UpdateValue(self.__position)

    def GetGoodText(self):
        return self.__goodText
    
    def GetBadText(self):
        return self.__badText
    
    def Target(self, turret:Slave, turretPosition:float):
        distance = abs(self.GetPosition() - turretPosition)

        time = distance / 5.0
        SOUND_MODULE.PlayAimingSound()
        turret.SendSettingUpdateByName("SPEED TIME", int(time * 1000) )
        turret.SendSettingUpdateByName("POSITION", self.GetPosition())
        if distance != 0:
            self.WaitEndAimingNotif()

        SOUND_MODULE.Stop()

    def PrepareToDestroy(self) -> None:
        self.__layout = None
        self.__nameElement = None
        self.__positionElement = None
        self.__frameElement = None
        self.__goodText = None
        self.__badText = None

