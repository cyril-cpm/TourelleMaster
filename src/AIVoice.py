import pyttsx3
import openai
import threading
import queue

### SPEAKING PROCESS ###

def speakingProcessFunction(queue:queue.Queue):
    engine = pyttsx3.init()
    engine.setProperty('volume', 1)

    voices = engine.getProperty('voices')

    for voice in voices:
        if "French" in voice.name:
            engine.setProperty("voice", voice.id)
            break

    while True:
        sentence, isQuestion = queue.get()
        engine.say(sentence)
        engine.runAndWait()
        queue.task_done()



class AIVoice():
    def __init__(self, speakingQueue:queue.Queue):
        api_key = ""
        with open("openai_api_key.txt") as apiKeyFile:
            api_key = apiKeyFile.read()

        self.__openai = openai.OpenAI(api_key=api_key)

        self.__preprompt = ""
        with open("openai_preprompt.txt", encoding="utf-8") as prepromptFile:
            self.__preprompt = prepromptFile.read()
        self.__memory = []
        self.__model = "gpt-4o-mini"

        self.__speakingQueue = speakingQueue

        self.__speakingThread = threading.Thread(target=speakingProcessFunction, args=(self.__speakingQueue,), name="SpeakingThread")
        self.__speakingThread.start()

    def MakeRequest(self, content:str) -> str:
        messages = []
        messages.append({"role": "system", "content": self.__preprompt})

        for msg in self.__memory:
            messages.append({"role": "assistant", "content": msg})

        messages.append({"role": "user", "content": content})

        completion = self.__openai.chat.completions.create(model=self.__model, messages=messages)

        self.__memory.append(content)
        self.__memory.append(completion.choices[0].message.content)

        return completion.choices[0].message.content