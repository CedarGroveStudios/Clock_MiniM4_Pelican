# clock_miniM4_14x4LED.py  2020-03-29_v01)
# Cedar Grove Studios
# for 14x4 LED display and rotary encoder time setter
# uses cedargrove_unit_converter library
# uses cedargrove_clock_builder library (display, set_time, chime)

import time
import board
import neopixel as neo  # Feather M4
from   simpleio import map_range, tone
import adafruit_ds3231
from   analogio import AnalogIn
from   cedargrove_unit_converter.chronos           import adjust_dst
from   cedargrove_clock_builder.repl_display       import ReplDisplay
# from   cedargrove_clock_builder.pybadge_display    import PyBadgeDisplay  # PyBadge display
from   cedargrove_clock_builder.led_14x4_display   import Led14x4Display  # 14-segment LED
# from   cedargrove_clock_builder.led_7x4_display    import Led7x4Display   # 7-segment LED
# from   cedargrove_clock_builder.bigled_7x4_display import BigLed7x4Display   # 7-segment LED

i2c = board.I2C()
ds3231 = adafruit_ds3231.DS3231(i2c)

# PyBadge battery monitor
# batt = AnalogIn(board.A6)

# Feather M4 battery monitor and piezo
batt = AnalogIn(board.VOLTAGE_MONITOR)

# Feather M4 NeoPixel, purple indicator
pixel = neo.NeoPixel(board.NEOPIXEL,1, brightness=0.01, auto_write=False)
pixel[0] = (200, 0, 200)
pixel.write()
time.sleep(0.1)

print("Battery: {:01.2f} volts".format((batt.value / 65520) * 6.6))

### SETTINGS ###
clock_display  = ["led", "repl"]  # List of active display(s)
clock_zone     = "Pacific"  # Name of local time zone
clock_24_hour  = False      # 24-hour clock = True; 12-hour AM/PM = False
clock_auto_dst = True       # Automatic US DST = True
clock_sound    = False      # Sound is active = True
clock_tick     = True       # One-second tick sound

### Instatiate displays

#  4-digit 14-segment LED alphanumeric display
led_disp = Led14x4Display(clock_zone, clock_24_hour, clock_auto_dst,
                          clock_sound, brightness=0.5, debug=False)

"""#  4-digit 7-segment LED alphanumeric display
led_disp  = Led7x4Display(clock_zone, clock_24_hour, clock_auto_dst,
                          clock_sound, brightness=1.0, debug=False)"""

"""#  4-digit 7-segment LED alphanumeric display
led_disp  = BigLed7x4Display(clock_zone, clock_24_hour, clock_auto_dst,
                          clock_sound, brightness=1.0, debug=False)"""

"""# PyBadge display
pybadge_disp  = PyBadgeDisplay(clock_zone, clock_24_hour, clock_auto_dst,
                               clock_sound, brightness=0.5, debug=False
# pybadge_disp.battery = (batt.value / 65520) * 6.6"""

#  REPL display
repl_disp = ReplDisplay(clock_zone, clock_24_hour, clock_auto_dst,
                        clock_sound, debug=False)

### Instatiate time setter
# (none)

### Instatiate chimes
# (none)

### HELPERS ###

# Manually set time upon RTC power failure
if ds3231.lost_power:
    print("--RTC POWER FAILURE--")
    # Set time with REPL
    # ds3231.datetime = repl_disp.set_datetime()

    # Set time with PyBadge
    pybadge_disp.show(ds3231.datetime)
    pybadge_disp.message = "-RTC POWER FAILURE-"

    # Set time with LED with rotary encoder
    led_disp.message = "FAIL"

min_flag = half_flag = hour_flag = False

# initiate display contents

# Check datetime and adjust if DST
if clock_auto_dst:             # read the RTC and adjust for DST
    current, is_dst = adjust_dst(ds3231.datetime)
else:
    current = ds3231.datetime  # otherwise, just read the RTC
    is_dst = False

if "pybadge" in clock_display:
    pybadge_disp.dst = is_dst
    pybadge_disp.show(current)

if "led" or "big_led" in clock_display:
    if "led" in clock_display:
        led_disp.message = "CG MiniM4L CLOCK"
    led_disp.dst = is_dst
    led_disp.show(current)

while True:
    # Check datetime and adjust if DST
    if clock_auto_dst:             # read the RTC and adjust for DST
        current, is_dst = adjust_dst(ds3231.datetime)
    else:
        current = ds3231.datetime  # otherwise, just read the RTC
        is_dst = False

    # update REPL display
    if "repl" in clock_display:
        repl_disp.dst = is_dst
        repl_disp.show(current)

    # update led display
    if "led" or "big_led" in clock_display:
        led_disp.colon  = not led_disp.colon

        # Check to see if time was set
        new_xst_datetime, clock_sound, update_flag = led_disp.set_datetime(ds3231.datetime)
        if update_flag:  # If so, update RTC Std Time with new datetime
           ds3231.datetime = new_xst_datetime
           print("RTC time was set")

        led_disp.dst    = is_dst
        led_disp.show(current)  # refresh LED display

        # Refresh FeatherM4 NeoPixel to show "second hand"
        r = int(map_range(current.tm_sec, 0, 45, 255, 100))
        g = int(map_range(current.tm_sec, 15, 59, 100, 255))
        b = int(map_range(current.tm_sec, 55, 59, 100, 255))
        pixel[0] = (r, g, b)
        pixel.write()

    if "pybadge" in clock_display:
        pybadge_disp.colon  = not pybadge_disp.colon  # auto-refresh

        # Check to see if time was set
        new_xst_datetime, clock_sound, update_flag = pybadge_disp.set_datetime(ds3231.datetime)
        if update_flag:  # If so, update RTC Std Time with new datetime
           ds3231.datetime = new_xst_datetime
           print("RTC time was set")

    # play tick sound
    if "pybadge" in clock_display:
        if clock_sound and clock_tick:
            pybadge_disp.tick()

    if "led" or "big_led" in clock_display:
        if clock_sound and clock_tick:
            led_disp.tick()

    # Do something every minute
    if current.tm_sec == 0 and not min_flag:
        # do something here
        print("every MIN")

        print("Battery: {:01.2f} volts".format((batt.value / 65520) * 6.6))

        # update PyBadge display
        if "pybadge" in clock_display:
            pybadge_disp.dst = is_dst
            pybadge_disp.show(current)
            pybadge_disp.battery = (batt.value / 65520) * 6.6

        # Display date on LED display
        if "led" or "big_led" in clock_display:
            led_disp.dst = is_dst
            led_disp.show(current, date=True)

        min_flag = True
    elif current.tm_sec > 0:
        min_flag = False

    # Do something every half-hour
    if current.tm_min == 30 and not half_flag:
        # do something here
        print("every HALF")
        half_flag = True
    elif current.tm_min > 30:
        half_flag = False

    # Do something every hour
    if current.tm_min == 0 and not hour_flag:
        # do something here
        print("every HOUR")
        hour_flag = True
    elif current.tm_min > 0:
        hour_flag = False

    # wait a second before looping
    prev_sec = current.tm_sec
    while current.tm_sec == prev_sec:  # wait a second before looping
        current = ds3231.datetime
