from machine import Pin, Timer
from ubot_buzzer import Buzzer

class TurtleHAT():

    def _noRepeatIncrement(self):
        for i in range(len(self._noRepeatElapsed)):
            self._noRepeatElapsed[i] += 1
            if self._firstRepeat <= self._noRepeatElapsed[i]:
                del self._noRepeatButtons[i]
                del self._noRepeatElapsed[i]


    def _advanceCounter(self):
        self._clockPin.on()

        if 9 <= self._counterPosition:
            self._counterPosition = 0
        else:
            self._counterPosition += 1

        self._clockPin.off()


    def _getPressedButton(self):
        pressed = -1

        for i in range(10):
            # pseudo pull-down                      # DEPRECATED: New PCB design (2.1) will resolve this.
            if self._inputPin.value() == 1:         # DEPRECATED: New PCB design (2.1) will resolve this.
                self._inputPin.init(Pin.OUT)        # DEPRECATED: New PCB design (2.1) will resolve this.
                self._inputPin.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
                self._inputPin.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

            if self._inputPin.value() == 1:
                if pressed == -1:
                    pressed = self._counterPosition
                else:
                    pressed += 7 + self._counterPosition

            self._advanceCounter()

        self._advanceCounter()                # shift "resting position"

        if self._repeatPrevention:
            self._noRepeatIncrement()

        self._pressedList[self._pressedListIndex] = pressed
        self._pressedListIndex += 1
        if len(self._pressedList) <= self._pressedListIndex:
                self._pressedListIndex = 0

        errorCount = 0

        for i in range(len(self._pressedList)):
            count = self._pressedList.count(self._pressedList[i])

            if self._pressLength <= count:
                return self._pressedList[i]

            errorCount += count
            if self._maxError < errorCount:
                return -1


    def _saveCommand(self):
        try:
            pressed = self._getPressedButton()
            if pressed != -1 and not pressed in self._noRepeatButtons:
                self._commandList.append(pressed)

                if self._repeatPrevention:
                    self._noRepeatButtons.append(pressed)
                    self._noRepeatElapsed.append(0)

                self._pressedList = [-1] * (self._pressLength + self._maxError)
        except Exception as e:
            print(e)


    def peekCommands(self):
        return self._commandList


    def __init__(self, config):
        self._clockPin = Pin(config.get("turtleClockPin"), Pin.OUT)
        self._clockPin.off()

        self._inputPin = Pin(config.get("turtleInputPin"), Pin.OUT) # FUTURE: Pin(16, Pin.IN)
        self._inputPin.off()                                        # DEPRECATED: New PCB design (2.1) will resolve this.
        self._inputPin.init(Pin.IN)                                 # DEPRECATED: New PCB design (2.1) will resolve this.

        self._counterPosition  = config.get("turtleCounterPos")
        self._pressLength      = config.get("turtlePressLength")
        self._maxError         = config.get("turtleMaxError")

        self._firstRepeat      = config.get("turtleFirstRepeat")
        self._repeatPrevention = 0 < self._firstRepeat
        self._noRepeatButtons  = []
        self._noRepeatElapsed  = []

        self._timer             = Timer(-1)
        self._pressedListIndex  = 0
        self._pressedList       = [-1] * (self._pressLength + self._maxError)
        self._commandList       = []

        self._timer.init(period = 20, mode = Timer.PERIODIC, callback = lambda t:self._saveCommand())
