import multiprocessing
import csv
from Players import *
from AIVoice import *
from Target import *
from Sound import *
import threading
import queue
from Settingator import *
from QuestionAndScoreDisplay import *


NULL = 0
AUTO = 1
MANUAL = 2

GS_INIT = 0
GS_WAITING_TO_START = 1
GS_ABOUT_TO_READ = 2
GS_READING = 3
GS_WAITING = 4
GS_REWARDING = 5
GS_FINISHED = 6
GS_FINISHED_READING = 7
GS_FINISHED_REWARDING = 8
GS_INTRODUCING = 9
GS_SPEAKING = 10



RED_BUTTON = 13
GREEN_BUTTON = 12
YELLOW_BUTTON = 14
BLUE_BUTTON = 27

RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"
GREEN_COLOR = "#00FF00"
DEFAULT_BG_COLOR = "#64778D"
YELLOW_COLOR = "#EEEE00"

QUESTION_FILENAME = "question.csv"

AIMING_NOTIF = 0x10


class Game():
    def __init__(self, settingator, strLock:threading.RLock):
        self.__questionPool = []
        self.__question = 0
        self.__mode = NULL
        self.__speakingQueue = queue.Queue()
        
        self.__finishedReadingTimestamp = 0
        self.__currentQuestionGoodAnswer = 0
        self.__accelDone = False
        #self.__questionAndScoreDisplay = QuestionAndScoreDisplay()
        #display.AddStuffToClose(self.__questionAndScoreDisplay)
        self.__aiVoice = AIVoice(self.__speakingQueue)
        self.__nextStepAfterSpeak = 0
        self.__isRunning = True

        self.__str:Settingator = settingator
        self.__strLock = strLock
        self.__playerList:Players = Players(self.__str, self.__strLock)

        with self.__strLock:
            self.__str.AddNotifCallback(AIMING_NOTIF, lambda slaveID : TURRET.PutAimingNotif())

        self.__functionQueue = queue.Queue(maxsize=1)

        self.__canAnswer = False

    def run(self):
        while True:
            try:
                f, args = self.__functionQueue.get_nowait()
                f(*args)
            except queue.Empty:
                pass
            except queue.Full:
                pass

    def isRunning(self):
        return self.__isRunning

    def MakeAIVoiceRequest(self, request:str):
        return self.__aiVoice.MakeRequest(request)

    def DisplayQuestion(question, order):
        pass
        
    def Start(self, mode:int):
        if threading.current_thread().name != "GameThread":
            self.__functionQueue.put((self.Start, (mode,)))
            return

        self.__mode = mode

        #ControlColumnLayout.RemoveElement(startGameAutoButton)
        #ControlColumnLayout.RemoveElement(startGameManualButton)
        #display.UpdateLayout()

        allQuestion = []
        
        with open(QUESTION_FILENAME, encoding="utf-8") as questionFile:
            csvContent = csv.reader(questionFile, delimiter=';')

            for row in csvContent:
                allQuestion.append(row)

        random.seed(time.time())
        numberQuestion = allQuestion.__len__()

        for index in range(1, numberQuestion, 1):
            questionNo = random.randint(0, allQuestion.__len__() - 1)
            self.__questionPool.append(allQuestion[questionNo])
            allQuestion.remove(allQuestion[questionNo])

        if self.__mode == AUTO:
            playerListString = ""

            for index in range(1, self.__playerList.GetNumberOfOrderedPlayer() + 1):
                playerListString += self.__playerList.GetPlayerByOrder(index).GetName() + " "

            self.Say(self.__aiVoice.MakeRequest("Présentation: les joueurs sont " + playerListString))

        self.Handling()

    def Handling(self, arg=None):
        if threading.current_thread().name != "GameThread":
            self.__functionQueue.put((self.Handling, (None,)))
            return
        
        circularQuestionIndex = self.__question % 6

        if circularQuestionIndex < 6:
            self.AskQuestion()
            self.Reward()
        
        if circularQuestionIndex == 2:
            self.__scoreAnnounce(self.__playerList)
        elif circularQuestionIndex == 5:
            self.__scoreAnnounce(self.__playerList, True)

        self.__question += 1

        if circularQuestionIndex != 5:
            self.Handling()

        

        

    def AskQuestion(self):
        if threading.current_thread().name != "GameThread":
            self.__functionQueue.put((self.AskQuestion, (None,)))
            return

        if self.__question < self.__questionPool.__len__():
            self.__playerList.SendAll("BLUE LOADING")
            self.__playerList.SetAllBGColor(DEFAULT_BG_COLOR)
            answerOrder = dict()
            answerOrdered = False
            index = 0
            alreadyPulled = dict()

            while not answerOrdered:
                newIndex = random.randint(2, 5)

                if not newIndex in alreadyPulled:
                    answerOrder[index] = newIndex
                    alreadyPulled[newIndex] = True

                    if newIndex == 2:
                        self.__currentQuestionGoodAnswer = index

                    index += 1
                    
                    if index >= 4:
                        answerOrdered = True
            
            question = self.__questionPool[self.__question]

            
            self.__questionAndScoreDisplay.SetQuestion(question[1], question[answerOrder[0]], question[answerOrder[1]], question[answerOrder[2]], question[answerOrder[3]])
            questionStr = question[1] + " Réponse A: " + question[answerOrder[0]] + ", Réponse B: " + question[answerOrder[1]] + ", Réponse C: " + question[answerOrder[2]] + ", Réponse D: " + question[answerOrder[3]] + " ?"
            self.__canAnswer = True
            
            self.__playerList.ResetAnswered()
            
            self.Ask(questionStr)

            self.__finishedReadingTimestamp = time.time()
            
            SOUND_MODULE.PlayWaitingSound()

            while (not self.__playerList.AllAnswered()) and (time.time() - self.__finishedReadingTimestamp < 7):
                pass

            if not self.__playerList.AllAnswered():
                for playerIndex in range(1, self.__playerList.GetNumberOfOrderedPlayer() + 1):
                    player:Player = self.__playerList.GetPlayerByOrder(playerIndex)

                    if player.CanAnswer():
                        player.Send("RED ACCEL LOADING")

            while (not self.__playerList.AllAnswered()) and (time.time() - self.__finishedReadingTimestamp < 10):
                pass

            SOUND_MODULE.PlayEndWaitSound()
            time.sleep(1)
            self.__canAnswer = False

    def Reward(self):
        if threading.current_thread().name != "GameThread":
            self.__functionQueue.put((self.Reward, (None,)))
            return
        
        if self.__mode == AUTO:
            for playerIndex in range(1, self.__playerList.GetNumberOfOrderedPlayer() + 1):
                player:Player = self.__playerList.GetPlayerByOrder(playerIndex)
                self.RewardPlayer(player, self.__currentQuestionGoodAnswer == player.GetLastAnswer())

    def RewardPlayer(self, player:Player, goodAnswered:bool):
        TURRET.MoveToPosition(player.GetPosition())

        SOUND_MODULE.PlayCountdownSound()
        time.sleep(2)

        if goodAnswered:
            SOUND_MODULE.PlayGoodSound()
            player.IncreaseGood()
        else:
            SOUND_MODULE.PlayBadSound()
            TURRET.Shoot()
            player.IncreaseFail()
        
        time.sleep(2)


    def GetSpeakingQueue(self):
        return self.__speakingQueue

    def Ask(self, sentence:str):
        self._Speak(sentence, True)

    def Say(self, sentence:str, wait:bool = True):
        self._Speak(sentence, False)

    def CanAnswer(self):
        return self.__canAnswer

    def _Speak(self, sentence:str, isQuestion:bool = True):
        self.__speakingQueue.put((sentence, isQuestion))
        self.__speakingQueue.join()

    def SetScoreDisplay(self, orderedPlayers):
        self.__questionAndScoreDisplay.SetScore(orderedPlayers)

    def SetQuestionDisplay(self, question, ansA, ansB, ansC, ansD):
        self.__questionAndScoreDisplay.SetQuestion(question, ansA, ansB, ansC, ansD)

    def TestScoreAnnounce(self) -> None:
        self.__scoreAnnounce(self.__playerList)

    def __scoreAnnounce(self, playerList:Players, final:bool = False):
        unorderedPlayers = []

        requestString = ""

        for index in range(0, NUMBER_PLAYER):
            thePlayer:Player = playerList.GetPlayer(index)
            unorderedPlayers.append(thePlayer)

        orderedPlayers = []

        for index in range(0, NUMBER_PLAYER):
            highestScore = -100
            highestScoreIndex = 0

            for secondIndex in range(0, unorderedPlayers.__len__()):
                if highestScore < unorderedPlayers[secondIndex].GetScore():
                    highestScore = unorderedPlayers[secondIndex].GetScore()
                    highestScoreIndex = secondIndex

            orderedPlayers.append(unorderedPlayers[highestScoreIndex])

            requestString += unorderedPlayers[highestScoreIndex].GetName() +\
                    ": bonnes réponses: " + str(unorderedPlayers[highestScoreIndex].GetGood()) +\
                    " mauvaises réponses: " + str(unorderedPlayers[highestScoreIndex].GetBad()) +\
                    " total: " + str(unorderedPlayers[highestScoreIndex].GetScore()) + ". "

            unorderedPlayers.remove(unorderedPlayers[highestScoreIndex])

        annoucementString = self.__aiVoice.MakeRequest(requestString)

        self.SetScoreDisplay(orderedPlayers)
        self.Say(annoucementString)
        
    def AddPlayer(self, slave:Slave) -> None:
        self.__playerList.AddPlayer(slave)

    def AddOrderedPlayer(self, player:Player) ->None:
        self.__playerList.AddOrderedPlayer(player)

    def GetPlayer(self, num:int) -> Player:
        return self.__playerList.GetPlayer(num)
    
    def playerPressButton(self, slaveID:int, button:int):
        logString = "Slave "+str(slaveID) + " pressed button "

        if button == RED_BUTTON:
            logString += "red"
        elif button == GREEN_BUTTON:
            logString += "green"
        elif button == BLUE_BUTTON:
            logString += "blue"
        elif button == YELLOW_BUTTON:
            logString += "yellow"

        print(logString)

        player:Player = self.__playerList.GetPlayerBySlaveID(slaveID)

        if player != None:
            if player.CanAnswer() and self.CanAnswer():
                if button == RED_BUTTON:
                    player.SetLastAnswer(0)
                    player.SetFrameBGColor(RED_COLOR)

                elif button == GREEN_BUTTON:                
                    player.SetLastAnswer(1)
                    player.SetFrameBGColor(GREEN_COLOR)

                elif button == YELLOW_BUTTON:
                    player.SetLastAnswer(2)
                    player.SetFrameBGColor(YELLOW_COLOR)

                elif button == BLUE_BUTTON:
                    player.SetLastAnswer(3)
                    player.SetFrameBGColor(BLUE_COLOR)

                #display.Update()
                player.Send("BLUE FROZEN")

    def ResetScore(self):
        self.__playerList.ResetScore()

    def ResetPlayer(self):
        self.__playerList.ResetPlayer()

    def SetAllBGColor(self, color):
        self.__playerList.SetAllBGColor(color)

    def SetQADisplay(self, qaDisplay:QuestionAndScoreDisplay) -> None:
        self.__questionAndScoreDisplay = qaDisplay

    def GetPlayerList(self) -> Players:
        return self.__playerList