from signal import pause
from gpiozero import Button, DigitalInputDevice

import board
import digitalio
import adafruit_character_lcd.character_lcd as lcd

Button.was_held = False
clk_pin = 3
dt_pin = 2
select_button_pin = 21
select_button_two_pin = 20
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d7 = digitalio.DigitalInOut(board.D27)
lcd_d6 = digitalio.DigitalInOut(board.D22)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_columns = 16
lcd_rows = 2
test_counter = 0

locked = False
selected = [True, False, False]
to_change = [True, False, False]
options = ["f/", "sec", "iso"]
values = [0, 0, 0]

fstop_index = 4
fstops = ["1.4 ", " 2  ",  "2.8 ", " 4  ", "5.6 ", " 8  ", " 11 ", " 16 ", " 22 ", " 32 "]
shutter_index = 6
shutter = [" 1/2 ", " 1/4 ", " 1/8 ", " 15  ", " 30  ", " 60  ", " 125 ", " 250 ", " 500 ", "1000 "]
iso_index = 1
iso = [" 50  ", " 100 ", " 200 ", " 400 ", " 800 ", "1600 ", "3200 ", "6400 "]

lcd = lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
lcd.message = "Exposure Calculator"

separator_char = "|"


def setup():
    values[0] = fstops[fstop_index]
    values[1] = shutter[shutter_index]
    values[2] = iso[iso_index]
    update_screen()


def update_screen():
    if not locked:
        lcd.message = "{}{} |{}{} |{}{} \n{}{}{}{}{}".format(
            "*" if selected[0] else " ",
            options[0],
            "*" if selected[1] else " ",
            options[1],
            "*" if selected[2] else " ",
            options[2],
            values[0],
            separator_char,
            values[1],
            separator_char,
            values[2]
        )
    else:
        lcd.message = "{}{} |{}{} |{}{} \n{}{}{}{}{}".format(
            ">" if to_change[0] else "*" if selected[0] else " ",
            options[0],
            ">" if to_change[1] else "*" if selected[1] else " ",
            options[1],
            ">" if to_change[2] else "*" if selected[2] else " ",
            options[2],
            values[0],
            separator_char,
            values[1],
            separator_char,
            values[2]
        )


def get_new_value(index, clockwise):
    global fstop_index
    global shutter_index
    global iso_index
    if index is 0:
        if clockwise:
            fstop_index += 1
            if fstop_index > len(fstops) - 1:
                fstop_index = len(fstops) - 1
        else:
            fstop_index -= 1
            if fstop_index < 0:
                fstop_index = 0
        return fstops[fstop_index]
    elif index is 1:
        if clockwise:
            shutter_index += 1
            if shutter_index > len(shutter) - 1:
                shutter_index = len(shutter) - 1
        else:
            shutter_index -= 1
            if shutter_index < 0:
                shutter_index = 0
        return shutter[shutter_index]
    else:
        if clockwise:
            iso_index += 1
            if iso_index > len(iso) - 1:
                iso_index = len(iso) - 1
        else:
            iso_index -= 1
            if iso_index < 0:
                iso_index = 0
        return iso[iso_index]


def released(btn):
    if not btn.was_held:
        pressed()
    btn.was_held = False


def held(btn):
    btn.was_held = True
    global locked
    global separator_char
    locked = not locked
    if locked:
        separator_char = "="
    else:
        separator_char = "|"
    update_screen()


def pressed():
    changed = False
    for counter in range(0, 2):
        if selected[counter]:
            selected[counter] = False
            selected[counter+1] = True
            changed = True
            break

    if not changed:
        selected[2] = False
        selected[0] = True
    update_screen()


def second_button_pressed():
    # TODO: Change this method so that
    # selected one and two can't be the same
    if locked:
        changed = False
        for counter in range(0, 2):
            if to_change[counter]:
                to_change[counter] = False
                to_change[counter+1] = True
                changed = True
                break

        if not changed:
            to_change[2] = False
            to_change[0] = True

        update_screen()


def rot():
    index_to_update = 0
    for counter in range(0, 3):
        if selected[counter]:
            index_to_update = counter
            break

    clkstate = clk.value
    dtstate = dt.value

    if not locked:
        values[index_to_update] = get_new_value(index_to_update, clkstate is dtstate)

    update_screen()


button = Button(select_button_pin)
button.when_held = held
button.when_released = released

button_two = Button(select_button_two_pin)
button_two.when_activated = second_button_pressed

clk = DigitalInputDevice(clk_pin, True)
clkLastState = clk.value
dt = DigitalInputDevice(dt_pin, True)

clk.when_deactivated = rot

setup()

pause()
