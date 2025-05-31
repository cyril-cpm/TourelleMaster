import pygame.mixer as mx

class Sound:
    def __init__(self):
        ### Sound Management ###
        mx.init(channels=1)
        self.__channel = mx.Channel(0)
        self.__goodSound = mx.Sound("sound/good.wav")
        self.__badSound = mx.Sound("sound/bad.wav")
        self.__waitingSound = mx.Sound("sound/waiting.wav")
        self.__endWaitSound = mx.Sound("sound/endWait.wav")
        self.__countdownSound = mx.Sound("sound/shotCountdown2.wav")
        self.__aimingSound = mx.Sound("sound/aiming2.wav")

    def PlayAimingSound(self):
        self.__channel.play(self.__aimingSound, -1)

    def PlayCountdownSound(self):
        self.__channel.play(self.__countdownSound)

    def PlayGoodSound(self):
        self.__channel.play(self.__goodSound)

    def PlayBadSound(self):
        self.__channel.play(self.__badSound)

    def PlayWaitingSound(self):
        self.__channel.play(self.__waitingSound)

    def PlayEndWaitSound(self):
        self.__channel.play(self.__endWaitSound)

    def Stop(self):
        self.__channel.stop()

SOUND_MODULE = Sound()