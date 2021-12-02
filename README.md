# AquaControl
 A web application for Raspberry Pi aquarium tech!

Since this project controls my home devices, I provided a [video demo](https://youtu.be/Ijvt4syre6s) instead of a live website.
## What I wanted
Entertain myself during lockdown by automating some hobbies. I decided upon adding some lights to my aquarium which ultimately had me creating my own LED controller with a webserver for remote access. I tinkered with PHP in the past so I had a general idea of what I was doing, though I fancied a modern web framework this time.
## What it can do
* Change LED color and brightness, schedule on/off times
* Live stream video from camera
* Monitor water temperatures

There is potential for a lot more, this is just what I came up with.
## How I did it
I had a few Raspberry Pi's lying around, so I figured Python would be perfect for the job because I could self-host! It was between django and Flask—I chose the latter only because the pepper looked tasty. I like to start with the structure of the webpage so I can have a good idea of how I want to add the JavaScript functionality. I brushed up on my HTML skills and got to work.

The process of creating routes and handling data on the backend API was relatively straightforward once I figured out how requests work. GeeksForGeeks never fails to enthrall me with wisdom whenever I get stuck on something. I pondered making the webserver accessible on the internet so I also faced the challenge of user authentication. For this I wanted to include SQLite to store user credentials. I got lost in the cybersecurity aspect but I managed to add salt & pepper to passwords and store the hashes on a database. Most of the user interface communicates with the backend through AJAX calls.

## What I could improve
I have been learning a lot of cool new things since this was made. I can expand upon user authentication with Flask SQLAlchemy, redo styling with flex and SASS or utilize SMTP to email weekly reports. I'm experimenting with React now and want to give AquaControl a full makeover—maybe even learn React Native and Express.js to make an android application for my phone! I get carried away with ideas. For now, I will polish what I already have.

## What you need
* Raspberry Pi (tested with 3b+)
* Python 3 (tested with 3.8.7 and 3.7.3)
* WS2812B LED Strip (NeoPixel)
* DS18B20 Probe (for temperature data)
* PiCamera/Arducam (for live stream)

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
Time to setup AquaControl! Create an account that you will use to authenticate your requests. Run `users.py` for a simple interface that will guide you through it.
The menu should look like this
```
[1] Validate User
[2] Register User
[3] Delete User
[4] Exit
```
Select 2 to create a quick account. You will be prompted to provide a unique username and password. If you forget your password, you can simply select the delete user option and create another. You can change it later from the website.

You can also edit the PEPPER value in `users.py` for your password hashes.

Assuming you have everything wired by now, you should configure a few things before starting the server. Open `modules/leds.py` in an editor, then change the LED_PIN and NUM_PIXELS variables to the appropriate values for your use case.

Finally—to start recording data for the temperature graphs, you should setup a job to run `tracker.py` on startup. There are [several](https://www.itechfy.com/tech/auto-run-python-program-on-raspberry-pi-startup/) ways to do this. I did it by adding this at the bottom of rc.local
```
python3 /home/pi/git/projects/AquaControl/tracker.py 900 &
```
900 is a commandline argument specifying the amount of seconds to wait between each database write, so it saves the current temperatures every 15 minutes.

Now run `main.py` when you're ready and everything should be in working order—if not, please let me know! I hope my work can help someone out; I'm open to all feedback!
