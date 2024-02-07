# AquaControl
 A web application for Raspberry Pi controlling electrical circuits!
 
![aquacontrol](https://github.com/Tearrex/AquaControl/assets/26557969/a1fb35e7-70b0-40ec-84c8-9b4a00aabbe0)

Since this project controls my home devices, I provided a [video demo](https://youtu.be/Ijvt4syre6s) instead of a live website.
## What I wanted
Entertain myself during lockdown by automating some hobbies. I decided upon adding some lights to my aquarium which ultimately had me creating my own LED controller with a webserver for remote access.
## What it can do
* 💡 Change LED color and brightness, schedule on/off times
* 📷 Stream camera image capture 
* 🌡️ Monitor water temperatures

There is potential for a lot more, this is just what I came up with.
## How I did it
I had a few Raspberry Pi's lying around, so I figured Python would be perfect for the job. It was between django and Flask—I chose the latter only because the pepper looked tasty.

The process of creating routes and handling data on the backend API was relatively straightforward once I figured out how requests work. I pondered making the webserver accessible over the internet so I naturally learned about user authentication. I managed to hash passwords with salt & pepper and store them in an SQLite database. Most of the UI communicates with the backend through AJAX calls.

## What you need
* Raspberry Pi (tested with 3b+)
* Python 3
* WS2812B LED Strip
* DS18B20 Probe
* PiCamera/Arducam

Beyond the programming, you will have to wire everything together for these components. I recommend a breadboard kit for this—it's fun! There are tutorials online for the [WS2812B](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring) and [DS18B20](https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/) that break it down into clear steps.

To make it easy, I provided the `requirements.txt` file so you can install the necessary packages in a virtual environment.
On Windows, this can be done with
```
python -m venv envName
```
and activated with
```
envName\Scripts\activate.bat
```
now install the prerequisites
```
pip install -r requirements.txt
```
Time to setup AquaControl! Run `users.py` for a simple CLI that will help you create an authentication account.
The menu should look like this
```
[1] Validate User
[2] Register User
[3] Delete User
[4] Exit
```
Select 2 to create a quick account. You will be prompted to provide a unique username and password. If you forget your password, you can simply select the delete user option and create another. You can change your password from the website.

You can also edit the PEPPER value in `users.py` for your password hashes.

Assuming you have everything wired by now, you should configure a few things before starting the server. Open `modules/leds.py` in an editor, then change the `LED_PIN` and `NUM_PIXELS` variables to match your use case.

Finally—to start recording data for the temperature graphs, you should setup a job to run `tracker.py` on startup. There are [several](https://www.itechfy.com/tech/auto-run-python-program-on-raspberry-pi-startup/) ways to do this. I did it by adding this at the bottom of rc.local
```
python3 /home/pi/git/projects/AquaControl/tracker.py 900 &
```
900 is the amount of seconds to wait between each database write, so it captures the probe temperatures every 15 minutes.

Now run `main.py` when you're ready and everything should be in working order—if not, please let me know! I hope my work can help someone out; I'm open to all feedback!
