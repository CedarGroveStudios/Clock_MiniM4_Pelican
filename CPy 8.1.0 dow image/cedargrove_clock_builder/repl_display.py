# repl_display.py
# 2020-03-22 Cedar Grove Studios

import time

class ReplDisplay:

    def __init__(self, timezone="Pacific", hour_24_12=False, auto_dst=True,
                 sound=False, debug=False):
        #input parameters
        self._timezone   = timezone
        self._hour_24_12 = hour_24_12
        self._dst        = False
        self._auto_dst   = auto_dst
        self._sound      = sound
        self._message    = "REPL Clock"

        self._weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # debug parameters
        self._debug = debug
        if self._debug:
            print("*Init:", self.__class__)
            print("*Init: ", self.__dict__)

    @property
    def message(self):
        """Update the clock message text. Default is a blank message."""
        return self._message
    @message.setter
    def message(self, text=""):
        self._message = text

    @property
    def zone(self):
        """The clock's time zone. Default is Pacific."""
        return self._timezone
    @zone.setter
    def zone(self, timezone):
        self._timezone = timezone

    @property
    def hour_24(self):
        """Display 24-hour or 12-hour AM/PM. Default is 12-hour (False)."""
        return self._hour_24_12
    @hour_24.setter
    def hour_24(self, hour_24_12):
        self._hour_24_12 = hour_24_12

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
    def sound(self, sound=False):
        self._sound = sound

    def tick(self):
        print("<tick>")

    def alert(self, text=""):
        print("--ALERT--")
        print(text)

    def show(self, datetime):
        """Display time via REPL."""
        self._datetime = datetime

        if self._auto_dst and self._dst:  # changes the text to show DST
            flag_text = self._timezone[0] + "DT"
        else:  # or Standard Time
            flag_text = self._timezone[0] + "ST"

        hour = self._datetime.tm_hour  # Format for 24-hour or 12-hour output
        if self._hour_24_12:  # 24-hour
            am_pm = ""
        else:  # 12-hour clock with AM/PM
            am_pm = "AM"
            if hour >= 12:
                hour = hour - 12
                am_pm = "PM"
            if hour == 0:  # midnight hour fix
                hour = 12

        print("{} {}/{}/{}".format(self._weekday[self._datetime.tm_wday],
                                      self._datetime.tm_year,
                                      self._datetime.tm_mon,
                                      self._datetime.tm_mday))

        print("{}: {:02}:{:02}:{:02}".format(flag_text, hour,
                                             self._datetime.tm_min,
                                             self._datetime.tm_sec, am_pm,
                                             self._weekday[self._datetime.tm_wday]))
        return

    def set_datetime(self):
        """Manual input of time via REPL."""
        print("Enter time as 24-hour Standard Time")
        set_yr  = input("enter year (YYYY):")
        if set_yr == "":
            set_yr = int(2000)
        else:
            set_yr = max(2000, min(2037, int(set_yr)))

        set_mon = input("enter month (MM):")
        if set_mon == "":
            set_mon = 1
        else:
            set_mon = max(1, min(12, int(set_mon)))

        set_dom = input("enter day-of-month (DD):")
        if set_dom == "":
            set_dom = 1
        else:
            set_dom = max(1, min(31, int(set_dom)))

        set_hr  = input("enter 24-hour Standard Time hour (hh):")
        if set_hr == "":
            set_hr = 0
        else:
            set_hr = max(0, min(24, int(set_hr)))

        set_min = input("enter minute (mm):")
        if set_min == "":
            set_min = 0
        else:
            set_min = max(0, min(59, int(set_min)))

        # Build structured time:         ((year, mon, date, hour,
        #                                  min, sec, wday, yday, isdst))
        self._datetime = time.struct_time((set_yr, set_mon, set_dom, set_hr,
                                           set_min, 0, -1, -1, -1))

        # Fix weekday and yearday structured time errors
        self._datetime = time.localtime(time.mktime(self._datetime))
        return self._datetime
