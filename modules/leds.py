import os, time, schedule, threading, json
try:
    import board
    from neopixel import NeoPixel
except Exception:
    print("You are missing NeoPixel or not using a Raspberry Pi. Try creating a virtual environment.")
    input()
    exit()

LED_PIN = board.D18 # specify the data pin you connected to your strip
NUM_PIXELS = 25 # amount of LEDs on your strip
MAX_BRIGHTNESS = 25 # maximum brightness in percentage

PARENT_DIR = os.path.normpath(os.getcwd())
SETTINGS_PATH = os.path.join(PARENT_DIR, "aqua_config.json")
#print(SETTINGS_PATH)
class LEDs:
    # so far it can read the settings file 
    # but wont save changes that are applied, yet

    def get_settings(self):
        # defaults only used to make a new json file
        # your changes will be saved on top of this
        defaults = {
            "onTime": "00:00",
            "offTime": "00:00",
            "brightness": 0.05, # 5% brightness
            "colorR": 0,
            "colorG": 0,
            "colorB": 255
        }
        if not os.path.exists(SETTINGS_PATH):
            obj = json.dumps(defaults, indent=4)
            with open(SETTINGS_PATH, 'w') as out: out.write(obj)
            print("Created new settings file")
        with open(SETTINGS_PATH, 'r') as sett: return json.load(sett)

    def apply_settings(self):
        if self.settings["offTime"] != "00:00": self.set_timer("off", self.settings["offTime"], False)
        if self.settings["onTime"] != "00:00": self.set_timer("on", self.settings["onTime"], False)
        print("Settings applied")
    def __init__(self, raspberry):
        self.enabled = False # toggle for the LED strip
        self.settings = self.get_settings() # get user configuration
        print(self.settings)
        self.offThread = None
        self.onThread = None
        self.thread = threading.Thread(target=self.schedule_thread)
        self.thread.start()
        self.apply_settings()
        self.rainbow = True # LEDs will use wave effect by default
        
        self.color = (self.settings["colorR"],self.settings["colorG"],self.settings["colorB"])
        self.brightness = float(self.settings["brightness"])
        
        self.raspberry = raspberry
        if self.raspberry:
            self.pix = NeoPixel(LED_PIN, NUM_PIXELS, brightness=self.brightness, auto_write=False)
    def schedule_thread(self) -> None:
        """Checks the user's schedule every 2 minutes to see if it needs
        to toggle the LED lights."""
        print("Light scheduler thread is running!")
        while True:
            schedule.run_pending()
            time.sleep(120)
        print("Thread stopped!")
    def save_settings(self):
        with open(SETTINGS_PATH, 'w') as out:
            out.write(json.dumps(self.settings, indent=4))
    def set_timer(self, timer:str, _time:str, save:bool=True) -> None:
        """Used to toggle the LED lights at a scheduled time.\n
        Specify the timer you want to set as `on` or `off`,
        along with your desired `time` value."""
        if timer == "on":
            if _time == self.settings["onTime"]: return
            if not self.onThread:
                # make the thread
                self.onThread = schedule.every().day.at(_time).do(self.toggle, True, True)
                print(f"ON job set for {_time}")
            else:
                print("Cancelling old ON job...")
                schedule.cancel_job(self.onThread)
                self.onThread = schedule.every().day.at(_time).do(self.toggle, True, True)
                print(f"New ON job set for {_time}")
            self.settings["onTime"] = _time
        elif timer == "off":
            if _time == self.settings["offTime"]: return
            if not self.offThread:
                # make the thread
                self.offThread = schedule.every().day.at(_time).do(self.toggle, False, True)
                print(f"OFF job set for {_time}")
            else:
                print("Cancelling old OFF job...")
                schedule.cancel_job(self.offThread)
                self.offThread = schedule.every().day.at(_time).do(self.toggle, False, True)
                print(f"New OFF job set for {_time}")
            self.settings["offTime"] = _time
        else: return
        print(f"timer called. state: {timer} time: {_time}")
        if save: self.save_settings()
    def toggle(self, status:bool, force:bool=False) -> None:
        """Turn the LEDs on or off. The status should be `True` or `False`"""
        if self.enabled and not status or not status and force:
            if self.raspberry:
                self.pix.brightness = 0
                self.pix.fill((0,0,0))
                self.pix.show()
            self.enabled = False
            print("LEDs off")
        elif not self.enabled and status or status and force:
            if self.raspberry:
                self.pix.brightness = self.brightness
                if not self.rainbow:
                    self.pix.fill(self.color)
                    self.pix.show()
            self.enabled = True
            print("LEDs on")
    def set_brightness(self, amount) -> None:
        try: amount = float(amount)
        except ValueError: pass
        else:
            if amount > MAX_BRIGHTNESS:
                print(f"{amount}% is too strong of a brightness!! (Ignored)")
                return
            self.brightness = amount / 100
            if not self.enabled:
                print(f"Brightness changed to {amount}% but LEDs are off")
                return
            if self.raspberry:
                self.pix.brightness = self.brightness
                self.pix.show()
            print(f"Brightness now {self.brightness}")
    def set_color(self, color) -> None:
        #print(color)
        if len(color) == 3:
            self.rainbow = False
            self.color = color
            if self.raspberry:
                self.pix.fill(self.color)
                if self.enabled: self.pix.show()
            print(f"RGB set to: {color}")
        else: print("Received bad tuple for color change, must be (r,g,b)")

    # this is a standard effect from the NeoPixel library
    # you can find more online or try making one yourself
    # I couldn't figure out how they work
    def wheel(self, pos):
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)
    def rainbow_cycle(self, wait):
        for j in range(255):
            if not self.enabled or not self.rainbow:break
            for i in range(self.num_pixels):
                if not self.enabled or not self.rainbow: break
                rc_index = (i * 256 // self.num_pixels) + j
                self.pix[i] = self.wheel(rc_index & 255)
            if self.enabled and self.rainbow:
                self.pix.show()
                time.sleep(wait)
if __name__ == '__main__':
    print("This module is meant to be used by main.py\n"+
    "It only makes a rainbow wave effect by itself.")
    leds = LEDs()
    try:
        while True: leds.rainbow_cycle(0.03)
    except KeyboardInterrupt:
        leds.pix.fill((0,0,0))
        leds.pix.show()
        exit()