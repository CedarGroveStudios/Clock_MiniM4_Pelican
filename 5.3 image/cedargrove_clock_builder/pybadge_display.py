# pybadge_display.py
# 2020-03-21 Cedar Grove Studios

import time
import board
import displayio
from   adafruit_display_text.label import Label
from   adafruit_bitmap_font        import bitmap_font
import adafruit_imageload
from   adafruit_pybadger import pybadger
from   simpleio                    import map_range

class PyBadgeDisplay:

    def __init__(self, timezone="Pacific", hour_24=False, auto_dst=True,
                 sound=False, brightness=1.0, debug=False):
        # Input parameters
        self._timezone   = timezone
        self._hour_24_12 = hour_24
        self._dst        = False
        self._auto_dst   = auto_dst
        self._sound      = sound
        self._brightness = brightness

        # Other parameters
        self._message     = "PyBadge Clock"
        self._colon       = True
        self._batt_level  = 0   # Default battery level
        self._label_edits = []  # label edit attributes
        self._label_restore_color = []  # for restoring text color values

        self._weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self._month   = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                         "Sep", "Oct", "Nov", "Dec"]

        # Load the text font from the fonts folder
        self._font_0 = bitmap_font.load_font("/fonts/OpenSans-9.bdf")
        self._font_1 = bitmap_font.load_font("/fonts/Helvetica-Bold-36.bdf")

        # Instantiate PyBadger instance
        self.panel = pybadger
        self.panel._neopixels.brightness = 0.1  # Set default NeoPixel brightness
        self.panel.pixels.fill(0x000000)        # Clear all NeoPixels
        self.panel.play_tone(440, 0.1)          # A4 welcome tone

        # The board's integral display size and element size
        WIDTH  = board.DISPLAY.width   # 160 for PyGamer and PyBadge
        HEIGHT = board.DISPLAY.height  # 128 for PyGamer and PyBadge
        ELEMENT_SIZE = WIDTH // 4  # Size of element_grid blocks in pixels
        board.DISPLAY.brightness = self._brightness

        # Default colors
        self.BLACK   = 0x000000
        self.RED     = 0xFF0000
        self.ORANGE  = 0xFF8811
        self.YELLOW  = 0xFFFF00
        self.GREEN   = 0x00FF00
        self.CYAN    = 0x00FFFF
        self.BLUE    = 0x0000FF
        self.LT_BLUE = 0x000044
        self.VIOLET  = 0x9900FF
        self.DK_VIO  = 0x110022
        self.WHITE   = 0xFFFFFF
        self.GRAY    = 0x444455

        ### Define the display group ###
        self._image_group = displayio.Group(max_size=15)

        # Create a background color fill layer; image_group[0]
        self._color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
        self._color_palette = displayio.Palette(1)
        self._color_palette[0] = self.DK_VIO
        self._background = displayio.TileGrid(self._color_bitmap,
                                              pixel_shader=self._color_palette,
                                              x=0, y=0)
        self._image_group.append(self._background)
        self._label_restore_color.append(self.DK_VIO)
        self._label_edits.append(None)

        # Battery indicator tile grid; image_group[1]
        self._sprite_sheet, self._palette = adafruit_imageload.load("/cedargrove_clock_builder/batt_sprite_sheet.bmp",
                                                                    bitmap=displayio.Bitmap,
                                                                    palette=displayio.Palette)
        self._batt_icon = displayio.TileGrid(self._sprite_sheet,
                                             pixel_shader=self._palette,
                                             width = 1, height = 1,
                                             tile_width = 16, tile_height = 16)
        self._batt_icon.x = WIDTH - 16
        self._batt_icon.y = 1
        self._image_group.append(self._batt_icon)
        self._label_restore_color.append(self.BLACK)
        self._label_edits.append(None)

        ### Define labels and values using element grid coordinates
        # Colon; image_group[2]
        self._clock_digits_colon = Label(self._font_1, text=":",
                                         color=self.WHITE, max_glyphs=1)
        self._clock_digits_colon.x = 62
        self._clock_digits_colon.y = (HEIGHT // 2) + 10 - 3
        self._image_group.append(self._clock_digits_colon)
        self._label_restore_color.append(self._clock_digits_colon.color)
        self._label_edits.append(None)

        # Weekday; image_group[3]
        self._clock_wday = Label(self._font_0, text="---",
                                 color=self.YELLOW, max_glyphs=3)
        self._clock_wday.x = 21
        self._clock_wday.y = 40
        self._image_group.append(self._clock_wday)
        self._label_restore_color.append(self._clock_wday.color)
        self._label_edits.append(None)

        # Comma for Month Day (date); image_group[4]
        self._clock_comma = Label(self._font_0, text=",",
                                  color=self.YELLOW, max_glyphs=1)
        self._clock_comma.x = 99
        self._clock_comma.y = 40
        self._image_group.append(self._clock_comma)
        self._label_restore_color.append(self._clock_comma.color)
        self._label_edits.append(None)

        # AM/PM indicator; image_group[5]
        self._clock_ampm = Label(self._font_0, text="--",
                                 color=self.WHITE, max_glyphs=2)
        self._clock_ampm.x = 120
        self._clock_ampm.y = (HEIGHT // 2) + 10 - 8
        self._image_group.append(self._clock_ampm)
        self._label_restore_color.append(self._clock_ampm.color)
        self._label_edits.append(None)

        # Time Zone indicator; image_group[6]
        self._clock_dst = Label(self._font_0, text="---",
                                color=self.VIOLET, max_glyphs=3)
        self._clock_dst.x = 120
        self._clock_dst.y = (HEIGHT // 2) + 10 + 8
        self._image_group.append(self._clock_dst)
        self._label_restore_color.append(self._clock_dst.color)
        self._label_edits.append(None)

        # Sound indicator; image_group[7]
        self._clock_sound = Label(self._font_0, text="-----",
                                  color=self.VIOLET, max_glyphs=5)
        self._clock_sound.x = 5
        self._clock_sound.y = HEIGHT - 8
        self._image_group.append(self._clock_sound)
        self._label_restore_color.append(self._clock_sound.color)
        self._label_edits.append(("boolean", 0, 1))

        # Automatic DST indicator; image_group[8]
        self._clock_auto_dst = Label(self._font_0, text="-------",
                                     color=self.VIOLET, max_glyphs=7)
        self._clock_auto_dst.x = 104
        self._clock_auto_dst.y = HEIGHT - 8
        self._image_group.append(self._clock_auto_dst)
        self._label_restore_color.append(self._clock_auto_dst.color)
        self._label_edits.append(("boolean", 0 , 1))

        # Month; image_group[9]
        self._clock_month = Label(self._font_0, text="---",
                                  color=self.YELLOW, max_glyphs=3)
        self._clock_month.x = 55
        self._clock_month.y = 40
        self._image_group.append(self._clock_month)
        self._label_restore_color.append(self._clock_month.color)
        self._label_edits.append(("month", 1, 12))

        # Month Day (date); image_group[10]
        self._clock_mday = Label(self._font_0, text="--",
                                 color=self.YELLOW, max_glyphs=2)
        self._clock_mday.x = 83
        self._clock_mday.y = 40
        self._image_group.append(self._clock_mday)
        self._label_restore_color.append(self._clock_mday.color)
        self._label_edits.append(("int2", 1, 31))

        # Year; image_group[11]
        self._clock_year = Label(self._font_0, text="----",
                                 color=self.YELLOW, max_glyphs=4)
        self._clock_year.x = 105
        self._clock_year.y = 40
        self._image_group.append(self._clock_year)
        self._label_restore_color.append(self._clock_year.color)
        self._label_edits.append(("int4", 2000, 2037))

        # Hour; image_group[12]
        self._clock_digits_hour = Label(self._font_1, text="--",
                                        color=self.WHITE, max_glyphs=2)
        self._clock_digits_hour.x = 20
        self._clock_digits_hour.y = (HEIGHT // 2) + 10
        self._image_group.append(self._clock_digits_hour)
        self._label_restore_color.append(self._clock_digits_hour.color)
        self._label_edits.append(("int2", 0, 23))

        # Minutes; image_group[13]
        self._clock_digits_min = Label(self._font_1, text="--",
                                       color=self.WHITE, max_glyphs=2)
        self._clock_digits_min.x = 74
        self._clock_digits_min.y = (HEIGHT // 2) + 10
        self._image_group.append(self._clock_digits_min)
        self._label_restore_color.append(self._clock_digits_min.color)
        self._label_edits.append(("int2", 0, 59))

        # Clock Message area; image_group[14]
        self._clock_message = Label(self._font_0, text="",
                                 color=self.VIOLET, max_glyphs=20)
        self._clock_message.x = 5
        self._clock_message.y = 5
        self._image_group.append(self._clock_message)
        self._label_restore_color.append(self._clock_message.color)
        self._label_edits.append(None)

        # debug parameters
        self._debug = debug
        if self._debug:
            print("*Init:", self.__class__)
            print("*Init: ", self.__dict__)

    @property
    def message(self):
        """Update the clock's message text. Default is a blank message."""
        return self._clock_message.text
    @message.setter
    def message(self, text=""):
        self._message = text[:20]

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
    def dst(self, dst=False):
        self._dst = dst

    @property
    def auto_dst(self):
        """Automatically display US DST. Default is auto DST (True)."""
        return self._auto_dst
    @auto_dst.setter
    def auto_dst(self, auto_dst=True):
        self._auto_dst = auto_dst

    @property
    def sound(self):
        """Sound is activated. Default is no sound (False)."""
        return self._sound
    @sound.setter
    def sound(self, sound=False):
        self._sound = sound

    @property
    def brightness(self):
        """Display brightness (0 - 1.0). Default is full brightness (1.0)."""
        return self._brightness
    @brightness.setter
    def brightness(self, brightness=1.0):
        self._brightness = brightness
        board.DISPLAY.brightness = self._brightness

    @property
    def colon(self):
        """Display the colon."""
        return self._colon
    @colon.setter
    def colon(self, colon=True):
        """Display the colon. Default is display colon (True)."""
        self._colon = colon
        if self._colon:
            self._clock_digits_colon.text = ":"
        else:
            self._clock_digits_colon.text = ""

    @property
    def battery(self):
        """Display the battery icon."""
        return self._batt_level
    @battery.setter
    def battery(self, volts=0):
        """Display the battery icon. Default is zero volts (0)"""
        self._batt_volts   = volts
        self._batt_level   = int(map_range(self._batt_volts, 3.35, 4.15, 0, 5))
        self._batt_icon[0] = self._batt_level

    def tick(self):
        """Play tick sound."""
        self.panel.play_file("/cedargrove_clock_builder/tick_soft.wav")
        return

    def alert(self, text=""):
        """Place alert message in clock message area. Default is the previous message."""
        self._msg_text = text[:20]
        if self._msg_text == "":
            self._clock_message.text = self._message
        else:
            self._clock_message.color = self.RED
            self._clock_message.text = self._msg_text
            self.panel.play_tone(880, 0.100)  # A5
            self._clock_message.color = self.YELLOW
            self.panel.play_tone(880, 0.100)  # A5
            self._clock_message.color = self.RED
            self.panel.play_tone(880, 0.100)  # A5
            self._clock_message.color = self.YELLOW
            time.sleep(1)
            self._clock_message.color = self.VIOLET

    def show(self, datetime):
        """Display time via REPL. The primary function of this class."""
        self._datetime = datetime  # xST structured time object

        if self._auto_dst and self._dst:  # changes the text to show DST
            self._clock_dst.text = self._timezone[0] + "DT"
        else:  # or Standard Time
            self._clock_dst.text = self._timezone[0] + "ST"

        if self._auto_dst:
            self._clock_auto_dst.text = "AutoDST"
        else:
            self._clock_auto_dst.text = ""

        self._hour = self._datetime.tm_hour  # Format 24-hour or 12-hour output
        if self._hour_24_12:  # 24-hour
            self._clock_ampm.text = "  "
        else:  # 12-hour clock with AM/PM
            self._clock_ampm.text = "AM"
            if self._hour  >= 12:
                self._hour = self._hour - 12
                self._clock_ampm.text = "PM"
            if self._hour  == 0:  # midnight hour fix
                self._hour = 12

        if self._sound:
            self._clock_sound.text = "sFX"
        else:
            self._clock_sound.text = ""

        self._clock_message.text  = self._message
        self._clock_wday.text  = self._weekday[self._datetime.tm_wday]
        self._clock_month.text = self._month[self._datetime.tm_mon - 1]
        self._clock_mday.text  = "{:02d}".format(self._datetime.tm_mday)
        self._clock_year.text  = "{:04d}".format(self._datetime.tm_year)
        self._clock_digits_hour.text = "{:02d}".format(self._hour)
        self._clock_digits_min.text  = "{:02d}".format(self._datetime.tm_min)
        if self._colon:
            self._clock_digits_colon.text = ":"
        else:
            self._clock_digits_colon.text = ""
        board.DISPLAY.show(self._image_group)  # Load display
        time.sleep(0.1)  # Allow display to load
        return

    def _dim(self, color=0X0000FF):
        """Dim all image group text elements to BLUE."""
        for i in range(2, len(self._label_restore_color)):
            self._image_group[i].color = color
        return

    def _restore(self):
        """Restore all image group text elements to original colors."""
        for i in range(2, len(self._label_restore_color)):
            self._image_group[i].color = self._label_restore_color[i]
        return

    def set_datetime(self, xst_datetime):
        """Manual input of time via PyBadge DisplayIO."""
        self._xst_datetime = xst_datetime

        if not self.panel.button.start:
            # Return datetime, sound flag, and "no change" flag
            return self._xst_datetime, self._sound, False
        self.panel.play_tone(784, 0.030)  # G5
        while self.panel.button.start:
            pass

        self._dim()
        self._clock_digits_colon.text = ""
        self._clock_ampm.text         = ""
        self._clock_digits_hour.text  = "{:02}".format(self._xst_datetime.tm_hour)
        self._clock_dst.text          = "xST"
        self._clock_message.text         = "24-hr Standard Time"
        self._clock_message.color        = self.YELLOW
        if self._clock_sound.text == "":
            self._clock_sound.text    = "-OFF-"
        if self._clock_auto_dst.text == "":
            self._clock_auto_dst.text = "-OFF-"

        self._param_index = 0  # Reset index of parameter list
        # Select parameter to change
        while not self.panel.button.start:  # start button exits setup process
            while (not (self.panel.button.up or self.panel.button.down)) and (not self.panel.button.start):
                if self.panel.button.left:
                    self._param_index = self._param_index - 1
                if self.panel.button.right:
                    self._param_index = self._param_index + 1
                self._param_index = max(7, min(13, self._param_index))
                self._image_group[self._param_index].color = self.CYAN
                time.sleep(0.15)
                self._image_group[self._param_index].color = self.BLUE
                time.sleep(0.15)
            if self.panel.button.up or self.panel.button.down:
                self.panel.play_tone(1319, 0.030)  # E6

            # Adjust parameter value
            while (not (self.panel.button.left or self.panel.button.right)) and (not self.panel.button.start):
                self._image_group[self._param_index].color = self.GREEN

                if self._label_edits[self._param_index][0] in ("int2", "int4"):
                    self._param_value = int(self._image_group[self._param_index].text)
                if self._label_edits[self._param_index][0] == "month":
                    self._param_value = self._month.index(self._image_group[self._param_index].text)
                if self._label_edits[self._param_index][0] == "boolean":
                    self._param_value = 0
                    if self._image_group[self._param_index].text in ("sFX", "AutoDST"):
                        self._param_value = 1

                if self.panel.button.up:
                    self._param_value = self._param_value + 1
                    self.panel.play_tone(880, 0.030)  # A5
                if self.panel.button.down:
                    self._param_value = self._param_value - 1
                    self.panel.play_tone(659, 0.030)  # E5

                # Get range from edits table
                if self._label_edits[self._param_index][0] == "int2":
                    self._image_group[self._param_index].color = self.GREEN
                    self._param_min   = self._label_edits[self._param_index][1]
                    self._param_max   = self._label_edits[self._param_index][2]
                    self._param_value = max(self._param_min,
                                            min(self._param_max, self._param_value))
                    self._image_group[self._param_index].text = str("{:02}".format(self._param_value))
                if self._label_edits[self._param_index][0] == "int4":
                    self._image_group[self._param_index].color = self.GREEN
                    self._param_min   = self._label_edits[self._param_index][1]
                    self._param_max   = self._label_edits[self._param_index][2]
                    self._param_value = max(self._param_min,
                                            min(self._param_max, self._param_value))
                    self._image_group[self._param_index].text = str("{:04}".format(self._param_value))
                if self._label_edits[self._param_index][0] == "month":
                    self._image_group[self._param_index].color = self.GREEN
                    self._param_min   = self._label_edits[self._param_index][1] - 1
                    self._param_max   = self._label_edits[self._param_index][2] - 1
                    self._param_value = max(self._param_min,
                                            min(self._param_max, self._param_value))
                    self._image_group[self._param_index].text = self._month[self._param_value]
                if self._label_edits[self._param_index][0] == "boolean":
                    self._param_min   = self._label_edits[self._param_index][1]
                    self._param_max   = self._label_edits[self._param_index][2]
                    self._param_value = max(self._param_min, min(self._param_max,
                                                                 self._param_value))
                    if self._param_value == 1:
                        self._image_group[self._param_index].color = self.GREEN
                        if self._param_index == 7:
                            self._image_group[self._param_index].text  = "sFX"
                            self._sound   = True
                        elif self._param_index == 8:
                            self._image_group[self._param_index].text  = "AutoDST"
                            self._auto_dst = True
                    else:
                        self._image_group[self._param_index].color = self.RED
                        if self._param_index == 7:
                            self._image_group[self._param_index].text  = "-OFF-"
                            self._sound   = False
                        elif self._param_index == 8:
                            self._image_group[self._param_index].text  = "-OFF-"
                            self._auto_dst = False
                time.sleep(.2)
            # optional: update changed flag only when a param value is changed
            self._image_group[self._param_index].color = self.BLUE

            if self.panel.button.left or self.panel.button.right:
                self.panel.play_tone(1319, 0.030)  # E6

        # Exit setup process
        if self.panel.button.start:           # Start button pressed
            self.panel.play_tone(784, 0.030)  # G5
        while self.panel.button.start:        # Wait for button release
            pass

        set_yr  = int(self._clock_year.text)
        set_mon = self._month.index(self._clock_month.text) + 1
        set_dom = int(self._clock_mday.text)
        set_hr  = int(self._clock_digits_hour.text)
        set_min = int(self._clock_digits_min.text)
        # Build structured time:             ((year, mon, date, hour,
        #                                      min, sec, wday, yday, isdst))
        self._xst_datetime = time.struct_time((set_yr, set_mon, set_dom, set_hr,
                                               set_min, 0, -1, -1, -1))
        # Fix weekday and yearday structured time errors
        self._xst_datetime = time.localtime(time.mktime(self._xst_datetime))

        self._clock_message.text = self._message  # restore clock message label
        self._restore()  # restore clock element colors

        # return with new datetime, sound flag, and "something changed" flag
        return self._xst_datetime, self._sound, True
