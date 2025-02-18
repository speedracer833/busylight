import array, time
from machine import Pin
import rp2
import config

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

class NeoPixel:
    def __init__(self, pin_num, num_leds, brightness=0.3):
        self.num_leds = num_leds
        self.brightness = brightness
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(pin_num))
        self.sm.active(1)
        self.ar = array.array("I", [0 for _ in range(num_leds)])
        self.width = config.MATRIX_WIDTH
        self.height = config.MATRIX_HEIGHT

    def _set_pixel(self, i, color):
        r = int(color[0] * self.brightness)
        g = int(color[1] * self.brightness)
        b = int(color[2] * self.brightness)
        self.ar[i] = (g << 16) + (r << 8) + b

    def set_pixel_xy(self, x, y, color):
        """Set pixel at x,y coordinates (0,0 is top-left)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            # Convert x,y to linear index
            i = y * self.width + x
            self._set_pixel(i, color)

    def fill_except_column(self, color, except_col):
        """Fill entire matrix except specified column with a color"""
        for y in range(self.height):
            for x in range(self.width):
                if x != except_col:
                    self.set_pixel_xy(x, y, color)

    def set_progress_column(self, col, remaining_minutes):
        """Set progress indicator in specified column"""
        max_minutes = config.MINUTES_PER_LED * self.height
        leds_to_light = min(self.height, remaining_minutes // config.MINUTES_PER_LED)
        
        # If we have overflow time, show all LEDs in overflow color
        if remaining_minutes > max_minutes:
            color = config.COLOR_OVERFLOW
            leds_to_light = self.height
        else:
            color = config.COLOR_PROGRESS
            
        # Fill column from bottom up
        for y in range(self.height):
            if y < leds_to_light:
                self.set_pixel_xy(col, self.height - 1 - y, color)
            else:
                self.set_pixel_xy(col, self.height - 1 - y, config.COLOR_OFF)

    def set_next_meeting_column(self, col, minutes_until):
        """Set next meeting countdown in specified column"""
        if minutes_until is None:
            # No upcoming meeting, turn off column
            for y in range(self.height):
                self.set_pixel_xy(col, y, config.COLOR_OFF)
            return
            
        max_minutes = config.MINUTES_PER_LED * self.height
        leds_to_light = min(self.height, minutes_until // config.MINUTES_PER_LED)
        
        # If next meeting is far away, show dimmed column
        if minutes_until > max_minutes:
            # Show full column in dimmed color
            color = tuple(int(c * 0.2) for c in config.COLOR_FREE)  # 20% brightness
            for y in range(self.height):
                self.set_pixel_xy(col, y, color)
        else:
            # Show countdown from top down (inverse of busy countdown)
            color = tuple(int(c * 0.5) for c in config.COLOR_FREE)  # 50% brightness
            for y in range(self.height):
                if y < leds_to_light:
                    self.set_pixel_xy(col, y, color)
                else:
                    self.set_pixel_xy(col, y, config.COLOR_OFF)

    def fill(self, color):
        for i in range(self.num_leds):
            self._set_pixel(i, color)
        self.show()

    def show(self):
        for pixel in self.ar:
            self.sm.put(pixel, 8)
        time.sleep_ms(10)

    def clear(self):
        self.fill(config.COLOR_OFF)

    def set_brightness(self, brightness):
        self.brightness = min(max(brightness, 0.0), 1.0) 