import time
import random
from Sound import *
from Settingator import *
from Setting import *
import queue
import threading

TP_START = 0.0
TP_END = 180.0

class Turret():
    def __init__(self):
        self.__allRewarded = False

        self.__kiddingSentence = ""
        self.__randomKidding = False
        self.__shouldKidding = False

        self.__turret:Slave = None
        self.__turretPositionSetting:Setting = None
        self.__aimingQueue = queue.Queue(1)

    def Init(self, turret:Slave):
        self.__turret = turret
        self.__turretPositionSetting = turret.GetSettingByName("POSITION")

        if self.__turretPositionSetting == None:
            print("FAIL TO GET TURRET POSITION SETTING")

    def PutAimingNotif(self) -> None:
        try:
            self.__aimingQueue.put(True, block=False)
        except queue.Full:
            print("AIMING QUEUE FULL")

    def WaitEndAimingNotif(self):
        self.__aimingQueue.get()

    def MoveToPosition(self, position:float) -> None:
        
        if (self.__turret == None or self.__turretPositionSetting == None):
            print("TURRET not defined")
            return

        if (position != self.__turretPositionSetting.GetValue()):
            SOUND_MODULE.PlayAimingSound()
            self.__turret.SendSettingUpdateByName("POSITION", position)
            self.WaitEndAimingNotif()         
            SOUND_MODULE.Stop()

    def Shoot(self) -> None:
        if (self.__turret == None):
            print("TURRET not defined")
            return
        
        self.__turret.SendSettingUpdateByName("SHOOT")

    def Reward(self, goodAnswer:int) -> bool:
        if self.__firstRewardCall:
            self.__firstRewardCall = False

            if self.__turretPos >= self.__numberPlayer / 2:
                self.__currentRewardingPlayerIncrementation = -1
                self.__currentRewardingPlayer = self.__numberPlayer - 1

            else:
                self.__currentRewardingPlayerIncrementation = +1
                self.__currentRewardingPlayer = 0

        if not self.__allRewarded:
            if TESTING and self.__targetDone == False:
                self.__targetDone = True
                self.__targetDoneTimestamp = time.time()

            if not self.__targetDone and not self.__targetting:
                self.TargetPlayer(None, self.__currentRewardingPlayer+1)
                SOUND_MODULE.PlayAimingSound()

            if self.__targetDone:
                if self.__randomKidding == False:
                    SOUND_MODULE.PlayCountdownSound()

                    self.__randomKidding = True

                    if random.randint(0, 2999) % 3 == 0:
                        self.__shouldKidding = True
                        playerToReward:Player = self.__playerList.GetPlayerByOrder(self.__currentRewardingPlayer+1)
                        shoot = playerToReward.GetLastAnswer() != goodAnswer

                        requestString = "Récompense: " + playerToReward.GetName() + " "
                        if shoot:
                            requestString += "se fait tirer dessus."
                        else:
                            requestString += "ne se fait pas tirer dessus."

                        self.__kiddingSentence = game.MakeAIVoiceRequest(requestString)


                if time.time() - self.__targetDoneTimestamp > 2:
                    playerToReward:Player = playerList.GetPlayerByOrder(self.__currentRewardingPlayer+1)
                    shoot = playerToReward.GetLastAnswer() != goodAnswer

                    if not shoot:
                        playerToReward.IncreaseGood()
                        playerToReward.Send("GREEN GOOD")
                        SOUND_MODULE.PlayGoodSound()
                    else:
                        playerToReward.IncreaseFail()
                        playerToReward.Send("RED BAD")
                        if not TESTING:
                            turret.SendSettingUpdateByName("SHOOT")
 
                        SOUND_MODULE.PlayBadSound()
                    
                    time.sleep(1)

                    if self.__shouldKidding:
                        game.Say(self.__kiddingSentence)
                        game.SetGameStep(GS_SPEAKING)
                        game.SetNextStepAfterSpeak(GS_REWARDING)

                    self.__kiddingSentence = ""
                    self.__shouldKidding = False
                    self.__randomKidding = False

                    self.__currentRewardingPlayer += self.__currentRewardingPlayerIncrementation
                    self.__targetDone = False

                    if self.__currentRewardingPlayer == self.__numberPlayer or self.__currentRewardingPlayer == -1:
                        self.__allRewarded = True

        else:
            self.__allRewarded = False


        if self.__allRewarded:
            self.__firstRewardCall = True

        return self.__allRewarded


TURRET:Turret = Turret()