from machine import Pin, Timer
from ubot_buzzer import Buzzer

class TurtleHAT():

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

            if pressed == self._lastPressed[0]:
                self._lastPressed[1] += 1
            else:
                self._lastPressed = [pressed, 1]

            if 0 < pressed and (self._lastPressed[1] == 1 or self._firstRepeat < self._lastPressed[1]):
                self._commandList.append(pressed)
                self._lastPressed[1] = 1
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

        self._lastPressed      = [0, 0]                             # [pressed button, elapsed (button check) cycles]
        self._firstRepeat      = config.get("turtleFirstRepeat")

        self._timer             = Timer(-1)
        self._pressedListIndex  = 0
        self._pressedList       = [0] * (self._pressLength + self._maxError)
        self._commandList       = commandList

        self._timer.init(period = config.get("turtleCheckPeriod"), mode = Timer.PERIODIC, callback = lambda t:self._saveCommand())
