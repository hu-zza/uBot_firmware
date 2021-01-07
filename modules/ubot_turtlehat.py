from machine import Pin, Timer
from ubot_buzzer import Buzzer

class TurtleHAT():

    def _noRepeatIncrement(self):
        length = len(self._noRepeatElapsed)

        for i in range(length):
            reversedIndex = length - 1 - i;
            self._noRepeatElapsed[reversedIndex] += 1

            if self._firstRepeat <= self._noRepeatElapsed[reversedIndex]:
                del self._noRepeatButtons[reversedIndex]
                del self._noRepeatElapsed[reversedIndex]


    def _advanceCounter(self):
        self._clockPin.on()

        if 9 <= self._counterPosition:
            self._counterPosition = 0
        else:
            self._counterPosition += 1

        self._clockPin.off()


    def _getPressedButton(self):
        pressed = 0

        for i in range(10):
            # pseudo pull-down                      # DEPRECATED: New PCB design (2.1) will resolve this.
            if self._inputPin.value() == 1:         # DEPRECATED: New PCB design (2.1) will resolve this.
                self._inputPin.init(Pin.OUT)        # DEPRECATED: New PCB design (2.1) will resolve this.
                self._inputPin.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
                self._inputPin.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

            if self._inputPin.value() == 1:
                pressed += pow(2, self._counterPosition)

            self._advanceCounter()

        # shift counter's "resting position" to the closest pressed button to eliminate BTN LED flashing
        if 0 < pressed:
            while bin(1024 + pressed)[12 - self._counterPosition] != "1":
                self._advanceCounter()

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
                return 0


    def _saveCommand(self):
        try:
            pressed = self._getPressedButton()
            if 0 < pressed and not pressed in self._noRepeatButtons:
                self._commandList.append(pressed)

                if self._repeatPrevention:
                    self._noRepeatButtons.append(pressed)
                    self._noRepeatElapsed.append(0)

                self._pressedList = [0] * (self._pressLength + self._maxError)
        except Exception as e:
            print(e)


    def __init__(self, config, commandList):
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
        self._pressedList       = [0] * (self._pressLength + self._maxError)
        self._commandList       = commandList

        self._timer.init(period = config.get("turtleCheckPeriod"), mode = Timer.PERIODIC, callback = lambda t:self._saveCommand())
