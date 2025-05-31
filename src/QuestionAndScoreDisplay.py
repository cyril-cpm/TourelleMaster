import threading
import PySimpleGUI as sg
import functools
import queue

RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"
GREEN_COLOR = "#00FF00"
YELLOW_COLOR = "#EEEE00"
DARK_GREY_COLOR = "#222222"
BLACK_COLOR = "#000000"
LIGHT_GREY_COLOR = "#666666"
GOLD_COLOR = "#D3AF37"
SILVER_COLOR = "#A8A9AD"
BRONZE_COLOR = "#49371B"
DARK_RED_COLOR = "#111111"
DEFAULT_BG_COLOR = "#64778D"

NUMBER_PLAYER = 3

_qaMainThreadQueue = queue.Queue()

def mainthread(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if threading.current_thread is threading.main_thread():
                return func(*args, **kwargs)
            else:
                _qaMainThreadQueue.put((func, args, kwargs))
        return wrapper


class QuestionAndScoreDisplay():
    def __init__(self):

        self.__PSGLayout = [[]]

        dummyWindow = sg.Window("",[[]], location=(-1, 0), finalize=True, size=(0,0), no_titlebar=True)
        dummyWindow.Maximize()

        self.__screenWidth, self.__screenHeight = dummyWindow.Size

        dummyWindow.Close()

        #### QUESTION DISPLAY ####

        questionDisplayLayout = [[],[]]

        self.__questionText = sg.Text("", background_color=DARK_GREY_COLOR, expand_x=True, justification="center")
        questionFrameLayout = [[sg.VPush(background_color=DARK_GREY_COLOR)], [self.__questionText], [sg.VPush(background_color=DARK_GREY_COLOR)]]
        questionFrame = sg.Frame("", questionFrameLayout, border_width=0, background_color=DARK_GREY_COLOR, expand_y=True, pad=10, size=(self.__screenWidth - 20, 1))

        self.__ansAText = sg.Text("", background_color=RED_COLOR, expand_x=True, justification="center")
        self.__ansBText = sg.Text("", background_color=GREEN_COLOR, expand_x=True, justification="center")
        self.__ansCText = sg.Text("", background_color=YELLOW_COLOR, expand_x=True, justification="center")
        self.__ansDText = sg.Text("", background_color=BLUE_COLOR, expand_x=True, justification="center")

        ansAFrame = sg.Frame("", [[sg.VPush(background_color=RED_COLOR)], [self.__ansAText], [sg.VPush(background_color=RED_COLOR)]], border_width=0, background_color=RED_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)
        ansBFrame = sg.Frame("", [[sg.VPush(background_color=GREEN_COLOR)], [self.__ansBText], [sg.VPush(background_color=GREEN_COLOR)]], border_width=0, background_color=GREEN_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)
        ansCFrame = sg.Frame("", [[sg.VPush(background_color=YELLOW_COLOR)], [self.__ansCText], [sg.VPush(background_color=YELLOW_COLOR)]], border_width=0, background_color=YELLOW_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)
        ansDFrame = sg.Frame("", [[sg.VPush(background_color=BLUE_COLOR)], [self.__ansDText], [sg.VPush(background_color=BLUE_COLOR)]], border_width=0, background_color=BLUE_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)

        self.__ansFrame = ansAFrame

        answerFrameLayout = [[],[]]
        answerFrameLayout[0].append(ansAFrame)
        answerFrameLayout[0].append(ansBFrame)
        answerFrameLayout[1].append(ansCFrame)
        answerFrameLayout[1].append(ansDFrame)

        answerFrame = sg.Frame("", answerFrameLayout, border_width=0, background_color=LIGHT_GREY_COLOR, size=(self.__screenWidth - 20,1), expand_y=True, pad=10)

        questionDisplayLayout[0].append(questionFrame)
        questionDisplayLayout[1].append(answerFrame)
        self.__questionDisplayFrame = sg.Column(questionDisplayLayout, expand_x=True, expand_y=True, background_color=BLACK_COLOR, pad=0, visible=False)

        self.__PSGLayout[0].append(self.__questionDisplayFrame)

        ########################

        #### SCORE DISPLAY #####

        self.__labelWidth = int(self.__screenWidth/1)
        self.__labelHeight = int(self.__screenHeight/4 - 20)

        length = sg.Text.string_width_in_pixels("_ 3000", "WWWWWWWWWWWWWWW")
        
        width = int(self.__labelWidth * 2.0/3.0)
        fontSize = int(3000 * (width / length))

        nameFont = "_ " + str(fontSize)
        scoreFont = "Inconsolata " + str(fontSize)

        scoreLayout = []
        
        self.__playersElements = []

        for index in range(0, NUMBER_PLAYER):
            playerElements = dict()

            playerElements['name'] = self.__newPlayerName(self.__colorFromIndex(index), nameFont)
            playerElements['good'] = self.__newPlayerScore(self.__colorFromIndex(index), GREEN_COLOR, scoreFont)
            playerElements['bad'] = self.__newPlayerScore(self.__colorFromIndex(index), RED_COLOR, scoreFont)
            playerElements['total'] = self.__newPlayerScore(self.__colorFromIndex(index), YELLOW_COLOR, scoreFont)

            scoreLayout.append([self.__newPlayerFrame(self.__colorFromIndex(index),
                                                      playerElements['name'],
                                                      playerElements['good'],
                                                      playerElements['bad'],
                                                      playerElements['total'])])
            
            self.__playersElements.append(playerElements)

        scoreFrame = sg.Frame("", scoreLayout, border_width=0, background_color=LIGHT_GREY_COLOR, size=(self.__labelWidth, 4 * (self.__labelHeight + 20)), element_justification="center")

        scoreDisplayLayout = [[sg.VPush(background_color=BLACK_COLOR)],
                              [scoreFrame],
                              [sg.VPush(background_color=BLACK_COLOR)]]

        self.__scoreDisplayFrame = sg.Frame("", scoreDisplayLayout, border_width=0, background_color=BLACK_COLOR, pad=0, element_justification="center", visible=False, size=(self.__screenWidth, self.__screenHeight))

        self.__PSGLayout[0].append(self.__scoreDisplayFrame)

        ########################

        ####### MAXIMIZE #######

        self.__maximizeButton = sg.Button("Maximize", key=self.__maximizeDisplay, visible=False)
        self.__PSGLayout[0].append(self.__maximizeButton)

        ########################

        self.__PSGWindow = sg.Window('Display', self.__PSGLayout, location=(-1, 0), grab_anywhere=True, element_justification='left', finalize=True, background_color=BLACK_COLOR, element_padding=0, return_keyboard_events=True, no_titlebar=True, size=(0, 0))
        self.__PSGWindow.Maximize()

        return
    
    def __newPlayerName(self, color, font):
        return sg.Text("", background_color=color, expand_x=True, font=font)
    
    def __newPlayerScore(self, bgColor, fgColor, font):
        return sg.Text("", background_color=bgColor, text_color=fgColor, font=font)
    
    def __newPlayerFrame(self, color, name, good, bad, total):
        return sg.Frame("", [[sg.VPush(background_color=color)],
                                 [sg.Column([[name, good, bad, total]], expand_x=True, pad=(40, 0), background_color=color)],
                                 [sg.VPush(background_color=color)]],
                                 background_color=color, size=(self.__labelWidth-20, self.__labelHeight), pad=10)

    def __colorFromIndex(self, index):
        if index == 0:
            return GOLD_COLOR
        if index == 1:
            return SILVER_COLOR
        if index == 2:
            return BRONZE_COLOR
        if index == 3:
            return DARK_RED_COLOR

    @mainthread
    def Update(self):
        event, values = self.__PSGWindow.read(0)
        if event == 'Escape:27':
            self.__PSGWindow.Close()
            #display.Close()

        if callable(event):
            event()

    @mainthread
    def SetQuestion(self, question:str, ansA:str, ansB:str, ansC:str, ansD:str):

        self.__scoreDisplayFrame.update(visible=False)
        self.__questionDisplayFrame.update(visible=True)
        self.__PSGWindow.read(0)

        part1 = ""
        part2 = ""

        questionCharLen = question.__len__()
        questionCharMid = int(questionCharLen / 2)

        for offset in range(0, questionCharMid):
            if question[questionCharMid + offset] == ' ':
                question = question[:questionCharMid + offset] + '\n' + question[questionCharMid + offset + 1:]
                part1 = question[:questionCharMid + offset]
                part2 = question[questionCharMid - offset + 1:]
                print("+ offset")
                break
            
            elif question[questionCharMid - offset] == ' ':
                question = question[:questionCharMid - offset] + '\n' + question[questionCharMid - offset + 1:]
                part1 = question[:questionCharMid + offset]
                part2 = question[questionCharMid - offset + 1:]
                print("- offset")
                break

        print(question)
        
        part1Length = sg.Text.string_width_in_pixels("_ 3000", part1)
        part2Length = sg.Text.string_width_in_pixels("_ 3000", part2)

        questionLength = part1Length if part1Length > part2Length else part2Length

        width = self.__screenWidth - 80
        fontSize = int(3000 * (width / questionLength))
        fontStr = "_ "+str(fontSize)
        print(fontStr)

        self.__questionText.update(value=question, font=fontStr)

        lengthA = sg.Text.string_width_in_pixels("_ 3000", ansA)
        lengthB = sg.Text.string_width_in_pixels("_ 3000", ansB)
        lengthC = sg.Text.string_width_in_pixels("_ 3000", ansC)
        lengthD = sg.Text.string_width_in_pixels("_ 3000", ansD)

        lengthiest = lengthA
        if lengthB > lengthiest:
            lengthiest = lengthB
        if lengthC > lengthiest:
            lengthiest = lengthC
        if lengthD > lengthiest:
            lengthiest = lengthD
        
        width = self.__screenWidth/2 - 80
        fontSize = int(3000 * (width / lengthiest))
        fontStr = "_ "+str(fontSize)

        height = sg.Text.char_height_in_pixels(fontStr)

        ansFrameWidth, ansFrameHeight = self.__ansFrame.get_size()

        ansFrameHeight = ansFrameHeight - 20

        if height > ansFrameHeight:
            fontSize = int(fontSize * (ansFrameHeight / height))
        fontStr = "_ "+str(fontSize)

        self.__ansAText.update(value=ansA, font=fontStr)
        self.__ansBText.update(value=ansB, font=fontStr)
        self.__ansCText.update(value=ansC, font=fontStr)
        self.__ansDText.update(value=ansD, font=fontStr)

    @mainthread
    def SetScore(self, orderedPlayers):

        for index in range(0, NUMBER_PLAYER):
            self.__playersElements[index]['name'].update(orderedPlayers[index].GetName())
            self.__transformAndUpdate(orderedPlayers[index].GetGood(), self.__playersElements[index]['good'])
            self.__transformAndUpdate(orderedPlayers[index].GetBad(), self.__playersElements[index]['bad'])
            self.__transformAndUpdate(orderedPlayers[index].GetScore(), self.__playersElements[index]['total'])

        self.__questionDisplayFrame.update(visible=False)
        self.__scoreDisplayFrame.update(visible=True)

        self.__PSGWindow.read(0)

    def __transformAndUpdate(self, value, sgText:sg.Text):
        valueStr = ""

        if value >= 10:
            valueStr = "  " + str(value)
        elif value >= 0:
            valueStr = "   " + str(value)
        elif value <= -10:
            valueStr = " " + str(value)
        elif value < 0:
            valueStr = "  " + str(value)

        sgText.update(valueStr)

    def __maximizeDisplay(self):
        self.__maximizeButton.update(visible=False)
        self.__PSGWindow.Maximize()

    @mainthread
    def Close(self):
        self.__PSGWindow.Close()
    
    def run(self):
        try:
            func, args, kwargs = _qaMainThreadQueue.get_nowait()
            if func is not None:
                func(*args, **kwargs)
        except queue.Empty:
            pass