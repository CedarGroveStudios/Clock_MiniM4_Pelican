# led_7x4_display.py
# Class for "standard" LED display with rotary encoder time set function
# 2020-07-05 Cedar Grove Studios

import time
import board
from digitalio                 import DigitalInOut, Direction, Pull
import rotaryio as enc
from adafruit_ht16k33.segments import BigSeg7x4
from simpleio                  import tone

class BigLed7x4Display:

    def __init__(self, timezone="Pacific", hour_24=False, auto_dst=True,
                 sound=False, brightness=1.0, address=0x70, debug=False):
        # Input parameters
        self._timezone   = timezone
        self._hour_24_12 = hour_24
        self._dst        = False
        self._auto_dst   = auto_dst
        self._sound      = sound
        self._colon      = True
        self._message    = "    "
        self._brightness = brightness
        self._address    = address

        self._param_list = [("1-12", 1, 12), ("1-31", 1, 31),
                            ("20--", 2010, 2037), ("0-23", 0, 23),
                            ("0-59", 0, 59), ("", 0, 1), ("", 1, 10),
                            ("----", 0, 0)]

        # Holder for parameter values
        self._param_val_list = [0, 0, 0, 0, 0, self._sound, int(self._brightness * 10)]

        # Rotary encoder
        self._sel_sw = DigitalInOut(board.D9)
        self._sel_sw.direction = Direction.INPUT
        self._sel_sw.pull = Pull.UP
        self._enc = enc.IncrementalEncoder(board.D6, board.D5)
        # Piezo speaker
        self._piezo = board.D13  # Shared with L13 LED
        # Display
        i2c = board.I2C()
        self._display = BigSeg7x4(i2c, address=self._address)
        self._display.brightness = brightness
        self._display.fill(0)  # Clear the display
        self._display.print("----")

        # Debug parameters
        self._debug = debug
        if self._debug:
            print("*Init:", self.__class__)
            print("*Init: ", self.__dict__)

    @property
    def message(self):
        """Update message text."""
        return self._message
    @message.setter
    def message(self, text=""):
        self._message = text

    @property
    def zone(self):
        """The clock's time zone. Default is Pacific."""
        return self._timezone
    @zone.setter
    def zone(self, timezone="Pacific"):
        self._timezone = timezone

    @property
    def hour_24(self):
        """Display 24-hour or 12-hour AM/PM. Default is 12-hour (False)."""
        return self._hour_24_12
    @hour_24.setter
    def hour_24(self, hour_24=False):
        self._hour_24_12 = hour_24

    @property
    def dst(self):
        """Time is US DST. Default is Standard Time (False)."""
        return self._dst
    @dst.setter
    def dst(self, dst):
        self._dst = dst

    @property
    def auto_dst(self):
        """Automatically display US DST. Default is auto DST (True)."""
        return self._auto_dst
    @auto_dst.setter
    def auto_dst(self, auto_dst):
        self._auto_dst = auto_dst

    @property
    def sound(self):
        """Sound is activated. Default is no sound (False)."""
        return self._sound
    @sound.setter
    def sound(self, sound):
        self._dst = sound

    @property
    def brightness(self):
        """Display brightness. Default is 1.0 (maximum)."""
        return self._brightness
    @brightness.setter
    def brightness(self, brightness=1.0):
        self._brightness = brightness

    @property
    def colon(self):
        """Display the colon."""
        return self._colon
    @colon.setter
    def colon(self, colon=True):
        """Display the colon."""
        self._colon = colon

    def alert(self, text=""):
        """Display alert message. Default is the previous message."""
        self._msg_text = text
        if self._msg_text != "":
            tone(self._piezo, 880, duration=0.5)
            self._message = text + "    "
            self._display.marquee(self._message, delay=0.2, loop=False)

    def _param_text(self, index=0):
        """ Display parameter index legend. """
        if index in (0, 1, 2, 3, 4, 7):
            self._display.print(self._param_list[self._param_index][0])
        if index == 5:
            # BEEP
            self._display.fill(0)
            self._display.set_digit_raw(0, 0b01111111)
            self._display.set_digit_raw(1, 0b01111001)
            self._display.set_digit_raw(2, 0b01111001)
            self._display.set_digit_raw(3, 0b01110011)
        if index == 6:
            # LED
            self._display.fill(0)
            self._display.set_digit_raw(0, 0b00000000)
            self._display.set_digit_raw(1, 0b00111000)
            self._display.set_digit_raw(2, 0b01111001)
            self._display.set_digit_raw(3, 0b01011110)
        return

    def tick(self):
        """Make tick sound via piezo."""
        tone(self._piezo, 256, duration=0.030)

    def show(self, datetime, date=False):
        """Display time via LED display."""
        self._datetime           = datetime
        self._display.brightness = self._brightness
        hour = self._datetime.tm_hour  # Format for 24-hour or 12-hour output

        if not self._hour_24_12:       # 12-hour
            if hour >= 12:
                hour = hour - 12
                self._display.top_left_dot    = True
                self._display.bottom_left_dot = False
            else:
                self._display.top_left_dot    = False
                self._display.bottom_left_dot = True
            if hour == 0:  # Midnight hour fix
                hour = 12
        else:
            self._display.top_left_dot    = False
            self._display.bottom_left_dot = False

        if not date:
            if self._colon:
                self._display.colon = True
            else:
                self._display.colon = False
            self._display.print("{:2}{:02}".format(hour, self._datetime.tm_min))
        else:
            self._clock_month = "{:02d}".format(self._datetime.tm_mon)
            self._clock_mday  = "{:02d}".format(self._datetime.tm_mday)
            self._clock_year  = "{:04d}".format(self._datetime.tm_year)
            self._clock_digits_hour = "{:2}".format(hour)
            self._clock_digits_min  = "{:02}".format(self._datetime.tm_min)

            self._display.marquee(self._clock_month +
                                  "-" + self._clock_mday + "-" +
                                  self._clock_year + "    ", delay=0.2,
                                  loop=False)
            time.sleep(0.5)
        return

    def set_datetime(self, xst_datetime):
        """Manual input of time using a rotary encoder."""
        self._xst_datetime  = xst_datetime
        self._display.colon = False

        if self._sel_sw.value:  # Select switch not pressed
            # return datetime, sound flag, and "no change" flag
            return self._xst_datetime, self._sound, False
        tone(self._piezo, 784, duration=0.300)  # G5 piezo
        while not self._sel_sw.value:  # Wait until switch is released
            pass

        self.show(self._xst_datetime, date=True)
        time.sleep(0.5)

        self._param_val_list[0] = self._xst_datetime.tm_mon
        self._param_val_list[1] = self._xst_datetime.tm_mday
        self._param_val_list[2] = self._xst_datetime.tm_year
        self._param_val_list[3] = self._xst_datetime.tm_hour
        self._param_val_list[4] = self._xst_datetime.tm_min
        if self._sound:
            self._param_val_list[5] = 1
        else:
            self._param_val_list[5] = 0
        self._param_index  = 0      # Reset index of parameter list
        self._enc.position = 0      # Reset encoder position value
        self._changed      = False  # Reset edit change flag

        # Select parameter to change
        self._t0 = time.monotonic()      # Start the 10-second timeout clock
        # While select switch not pressed
        while self._sel_sw.value and time.monotonic() - self._t0 < 10:
            self._t0 = time.monotonic()  # Reset the timeout clock
            # While select switch not pressed
            while self._sel_sw.value and time.monotonic() - self._t0 < 10:
                self._param_index = self._enc.position
                self._param_index = max(0, min(7, self._param_index))
                if self._enc.position != self._param_index:
                    self._t0 = time.monotonic()  # Reset the timeout clock
                self._enc.position = self._param_index

                ### Display parameter prompt
                self._param_text(self._param_index)
                time.sleep(0.15)

            # Select switch pressed
            tone(self._piezo, 880, duration=0.3)  # A5 piezo
            while not self._sel_sw.value:         # Wait for switch to release
                pass

            if self._param_index == 7:  # EXIT was selected
                self._t0 = 0            # Force process to skip value section

            # Adjust parameter value
            # While select switch not pressed
            while self._sel_sw.value and time.monotonic() - self._t0 < 10:

                # Parameter edits and actions
                self._t0 = time.monotonic()  # Start the timeout clock
                self._enc.position = self._param_val_list[self._param_index]
                # While select switch not pressed
                while self._sel_sw.value and time.monotonic() - self._t0 < 10:
                    self._param_value = self._enc.position
                    self._min = self._param_list[self._param_index][1]  # Min
                    self._max = self._param_list[self._param_index][2]  # Max
                    self._param_value = max(self._min, min(self._max, self._param_value))
                    if self._enc.position != self._param_value:
                        self._t0 = time.monotonic()  # Reset the timeout clock
                    self._enc.position = self._param_value

                    # Display parameter prompt
                    if self._param_index == 0:  # Month value
                        self._display.print("{:02d}  ".format(self._param_value))
                        self._changed = True
                    if self._param_index == 2:  # 4-digit year vallue
                        self._display.print("{:04d}".format(self._param_value))
                        self._changed = True
                    if self._param_index in [1,3,4]:
                        self._display.print("  {:02d}".format(self._param_value))
                        self._changed = True
                    if self._param_index == 5:  # Sound effects flag
                        if self._param_value == 1:
                            self._display.print("   1")
                        else:
                            self._display.print("   0")
                    if self._param_index == 6:  # Display _brightness
                        self._brightness = self._param_value / 10
                        self._display.brightness = self._brightness
                        self._display.print("  {:02d}".format(self._param_value))
                    time.sleep(0.2)
                    self._param_val_list[self._param_index] = self._param_value
                self._enc.position = self._param_index + 1  # Move to next param
                time.sleep(0.2)

            # Select switch pressed
            tone(self._piezo, 880, duration=0.3)  # A5 piezo
            while not self._sel_sw.value:  # Wait for select switch release
                pass
        time.sleep(0.2)

        # Exit setup process
        if not self._sel_sw.value:  # Select switch pressed
            pass
        while not self._sel_sw.value:  # Wait for select switch release
            pass
        self._sound = self._param_val_list[5]

        # Structured time: (year, mon, date, hour, min, sec, wday, yday, isdst)
        self._xst_datetime = time.struct_time((self._param_val_list[2],
                                               self._param_val_list[0],
                                               self._param_val_list[1],
                                               self._param_val_list[3],
                                               self._param_val_list[4],
                                               1, -1, -1, -1))
        # Fix weekday and yearday structured time errors
        self._xst_datetime = time.localtime(time.mktime(self._xst_datetime))

        if self._changed:
            self._display.marquee("-   ", delay=0.2, loop=False)
            self.show(self._xst_datetime, date=True)

        tone(self._piezo, 784, duration=0.3)  # G5 piezo

        # return with new datetime, sound flag, and "time was changed" flag
        return self._xst_datetime, self._sound, self._changed
