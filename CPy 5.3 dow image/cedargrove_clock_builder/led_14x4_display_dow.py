# led_14x4_display_dow.py
# Class for 14-segment LED display to show day of week
# 2020-07-23 Cedar Grove Studios

import time
import board
from adafruit_ht16k33.segments import Seg14x4

class Led14x4DisplayDOW:

    def __init__(self, timezone="Pacific", hour_24=False, auto_dst=True,
                 sound=False, brightness=1.0, address=0x70, debug=False):
        # Input parameters
        self._timezone   = timezone
        self._hour_24_12 = hour_24
        self._dst        = False
        self._auto_dst   = auto_dst
        self._sound      = sound
        self._brightness = brightness
        self._address    = address

        self._weekday    = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

        # Display
        i2c = board.I2C()
        self._display = Seg14x4(i2c, address=self._address)
        self._display.brightness = brightness
        self._display.fill(0)  # Clear the display
        self._display.print("----")
        self._display.show()

        # Debug parameters
        self._debug = debug
        if self._debug:
            print("*Init:", self.__class__)
            print("*Init: ", self.__dict__)

    @property
    def brightness(self):
        """Display brightness. Default is 1.0 (maximum)."""
        return self._brightness
    @brightness.setter
    def brightness(self, brightness=1.0):
        self._brightness = brightness


    def show_day_of_week(self, datetime):
        """Display day of week."""
        self._display.brightness = self._brightness
        self._datetime           = datetime
        self._clock_wday  = self._weekday[self._datetime.tm_wday]
        self._display.marquee(self._clock_wday + "    ", delay=0.2, loop=False)
        self._display.marquee(self._clock_wday[0:3], delay=0.1, loop=False)
        self._display.show()
        return
