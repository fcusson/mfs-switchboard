import digitalio
import analogio
import board
import usb_hid

# imports for HID devices
from adafruit_hid.gamepad import Gamepad
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# initiates HID devices objects
gp = Gamepad(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)

# set analog sticks variables
ax = analogio.AnalogIn(board.A2)
axMax = 56960

ay = analogio.AnalogIn(board.A0)
ayMax = 56480

az = analogio.AnalogIn(board.A1)
azMax = 56464

jsMin = -127
jsMax = 127

# rotary encoder variables
encoderInput = digitalio.DigitalInOut(board.GP17)
encoderClk = digitalio.DigitalInOut(board.GP16)

encoderInput.direction = digitalio.Direction.INPUT
encoderClk.direction = digitalio.Direction.INPUT

encoderInput.pull = digitalio.Pull.DOWN
encoderClk.pull = digitalio.Pull.DOWN

# oldClkValue = encoderClk.value

encoderSelectPins = (board.GP21, board.GP20, board.GP19, board.GP18)

encoderButtons = [digitalio.DigitalInOut(pin) for pin in encoderSelectPins]

for encoderButton in encoderButtons:
    encoderButton.direction = digitalio.Direction.INPUT
    encoderButton.pull = digitalio.Pull.DOWN

# buttons variables
buttonPins = (board.GP11, board.GP12, board.GP13, board.GP14, board.GP7, board.GP8,
              board.GP10, board.GP9, board.GP22, board.GP2, board.GP3, board.GP4,
              board.GP5, board.GP6)

gamepadButtons = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)

buttons = [digitalio.DigitalInOut(pin) for pin in buttonPins]
for button in buttons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.DOWN

def UpdateKeyCodes(switchList):

    adder = 1
    multiplier = 0

    if switchList[0].value:
        adder = 2

    if switchList[1].value:
        adder = 3

    if switchList[2].value:
        multiplier = 1

    if switchList[3].value:
        multiplier = 2

    matrixPos = adder + (multiplier * 3)

    if matrixPos == 1:
        return (Keycode.KEYPAD_ASTERISK, Keycode.KEYPAD_BACKSLASH)
    elif matrixPos == 2:
        return (Keycode.KEYPAD_ENTER, Keycode.KEYPAD_EQUALS)
    elif matrixPos == 3:
        return (Keycode.KEYPAD_FORWARD_SLASH, Keycode.KEYPAD_MINUS)
    elif matrixPos == 4:
        return (Keycode.KEYPAD_PLUS, Keycode.KEYPAD_ONE)
    elif matrixPos == 5:
        return (Keycode.KEYPAD_TWO, Keycode.KEYPAD_THREE)
    elif matrixPos == 6:
        return (Keycode.KEYPAD_FOUR, Keycode.KEYPAD_FIVE)
    elif matrixPos == 7:
        return (Keycode.KEYPAD_SIX, Keycode.KEYPAD_SEVEN)
    elif matrixPos == 8:
        return (Keycode.KEYPAD_EIGHT, Keycode.KEYPAD_NINE)
    elif matrixPos == 9:
        return (Keycode.KEYPAD_ZERO, Keycode.KEYPAD_PERIOD)

def CheckForPulse(newValue, oldValue, directionValue, keycodeList):

    global oldClkValue
    global encoderCounter
    global gp

    if not oldValue and newValue:
        oldClkValue = True
        if directionValue:
            kbd.send(keycodeList[0])
        else:
            kbd.send(keycodeList[1])

    elif oldValue and not newValue:
        oldClkValue = False

def RangeMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

while True:

    # update Keycode for rotary encoder
    encoderKeycodes = UpdateKeyCodes(encoderButtons)

    # Send encoder pulse if necessary
    CheckForPulse(encoderClk.value, oldClkValue, encoderInput.value, encoderKeycodes)

    # update joystick
    gp.move_joysticks(
        x=RangeMap(ax.value, 0, axMax, -127, 127),
        y=RangeMap(ay.value, 0, ayMax, -127, 127),
        z=RangeMap(az.value, 0, azMax, -127, 127),
    )

    # update button press
    for i, button in enumerate(buttons):
        if button.value:
            gp.press_buttons(gamepadButtons[i])
        else:
            gp.release_buttons(gamepadButtons[i])
