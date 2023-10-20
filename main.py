from flask import Flask, Response, render_template, request, jsonify, redirect, g, session, url_for
import datetime, time, platform, random, os, socket
import threading, cv2
from users import validate_password, hash_password
from tracker import sql_query, get_all_temps

app = Flask(__name__)
app.secret_key = 'YourSecretKey'
rasp = False
picam = None

# these IPs will bypass authentication for GET/POST requests
# this is just for my use case, you don't have to touch it.
IP_WHITELIST = []#["192.168.0.9"]

try:
    import board
    from neopixel import NeoPixel
except Exception as e: pass
else:
    # this is for the 1-wire protocol of the DS18B20 sensor
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    rasp = True

from modules.camera_pi import Camera
from modules.leds import LEDs
picam = Camera() # Camera Controller
leds = LEDs(rasp) # LED controller

# hacky approach but it will work for now
def parse_color(color):
    color = color.split('(')[1]
    return str(color).replace(',',' ').replace(')','')

@app.before_request
def before_request():
    """Checks for the client's session on the backend, provides basic authentication."""
    g.user = None
    if 'userid' in session: g.user = session['userid']

def gen():
    """Used to prep the picamera for the live video feed, it's just a sequence of continuous pictures."""
    while True:
        if picam.enabled:
            frame = picam.get_frame()
            yield (b'--frame\r\n' +
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else: break
plat = platform.system()
@app.route('/video_feed')
def video_feed():
    if not g.user: return ('No access')
    if picam.enabled:
        if plat == "Windows": 
            im = cv2.imread('static/resources/download.jpg')
            s, b = cv2.imencode('.jpg', im)
            frame = b.tobytes()
            bytes = b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
            return Response(bytes, mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/stream', methods=['GET', 'POST'])
def fish_stream():
    if request.method == 'POST':
        if not g.user: return ('No access')
        form = request.get_json(force=True)
        enabled = form["enabled"]
        if enabled == "true": picam.toggle_stream(True)
        elif enabled == "false": picam.toggle_stream(False)
        return (f'Stream set to {picam.enabled}')
    if not g.user: return redirect(url_for('login'))
    if picam.enabled:
        if plat == "Linux": url = url_for('video_feed')
        else: url = "static/resources/download.jpg"
    else: url = "static/resources/bblack.jpg"
    if picam.enabled:
        toggle = "checked"
        framedis = "none"
    else:
        toggle = ""
        framedis = "block"
    return render_template('stream.html', imgstream=url, senabled=toggle, framedisp=framedis)

local_ip = socket.gethostbyname(socket.gethostname())
@app.route('/changepass', methods=['GET', 'POST'])
def changepass():
    if not g.user: return redirect(url_for('login'))
    if request.method == 'POST':
        #session.pop('user', None)
        form = request.get_json(force=True)
        curpass = form['curpass']
        newpass = form['newpass']
        reppass = form['reppass']
        if newpass != reppass or newpass == reppass == "": return ('No match!')
        elif curpass == "": return ('incorrect!')
        user = sql_query("SELECT * FROM users WHERE user_id=(?)", True, False, (g.user,), 'users.db')
        if user:
            valid = validate_password(curpass, user[0][2])
            if valid:
                hashpass = hash_password(newpass)
                sql_query("UPDATE users SET password=(?), salt=(?) WHERE user_id=(?)", False, True, (hashpass[0],hashpass[1], g.user), 'users.db')
                return redirect(url_for('logout'))
            else:
                return ('incorrect!')
    return render_template('changepass.html')
# careful...
@app.route('/login', methods=['GET', 'POST'])
def login():
    #print(request.remote_addr)
    session.pop('user', None)
    if request.method == 'POST':
        form = request.get_json(force=True)
        username = form['username']
        password = form['password']
        query = sql_query("SELECT * FROM users WHERE username=(?)", True, False, (username,), 'users.db')
        if query:
            valid = validate_password(password, query[0][2])
            if valid:
                session['userid'] = query[0][0]
                return redirect(url_for('index'))
            else: return ('incorrect!')
        else: return ('incorrect!')
        return ('No')
    else:
        superb = request.args.get('superbland')
        if superb: return render_template('login.html', superbland=superb)
        else: return render_template('login.html', superbland='n')
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect(url_for('login', superbland='y'))
@app.route('/cleartemp', methods=['POST'])
def clear_temp():
    """Wipes all data from a temperature database.
    
    To clear water temps POST {'probe':'water'}
    To clear CPU temps POST {'probe':'cpu'}"""
    if not g.user and request.remote_addr != local_ip: return ('No access')
    if request.method == 'POST':
        #print(request.data)
        msg = request.get_json(force=True)
        if msg['probe'] == "water":
            sql_query("DELETE FROM temps", False, True)
            print("Cleared water data")
        elif msg['probe'] == "cpu":
            sql_query("DELETE FROM ctemps", False, True)
            print("Cleared cpu data")
        return (f'Cleared {msg["probe"]} data!')
@app.route('/changecol', methods=['POST'])
def change_col():
    """Change the LED color
    
    POST request should send JSON like this
    {`'color'`:`'(255,255,255)'`} the tuple being a string, no spaces."""
    if not g.user and request.remote_addr != local_ip: return ('No access')
    if request.method == 'POST':
        #print(request.data)
        msg = request.get_json(force=True)
        #print(msg)
        if msg["color"] == "rainbow":
            leds.rainbow = True
            print("Rainbow enabled")
            return ('None')
        newColor = parse_color(msg["color"])
        list = [int(i) for i in newColor.split(' ') if i.isdigit()]
        rgb = tuple(list)
        leds.rainbow = False
        leds.set_color(rgb)
        return ('None')
@app.route('/temps', methods=['GET'])
def temps():
    """Returns a JSON object with the CPU temperature in celcius
    and water temperature in fahrenheit"""
    if not request.remote_addr in IP_WHITELIST:
        if not g.user and request.remote_addr != local_ip: return ('No access')
    if request.method == 'GET':
        if platform.system() == "Linux":
            temps = get_all_temps()
            return jsonify({'ctemp':float(temps[1]), 'wtemp':temps[0]})
        else: return jsonify({'ctemp':random.randint(20,50), 'wtemp':random.randint(20,50)})
@app.route('/graphs')
def graphs():
    """Reads the temperature data and returns it as a JSON object
    to be rendered in the graphs.html template"""
    if not g.user and request.remote_addr != local_ip: return redirect(url_for('login'))
    wdata = sql_query("SELECT * FROM temps", True)
    wdates = [row[0] for row in wdata]
    wtemps = [row[1] for row in wdata]
    w_temps = sorted(wtemps)
    wlow = whigh = ''
    if w_temps:
        wlow = w_temps[0]
        whigh = w_temps[-1]
    cdata = sql_query("SELECT * FROM ctemps", True)
    cdates = [row[0] for row in cdata]
    ctemps = [row[1] for row in cdata]
    c_temps = sorted(ctemps)
    clow = chigh = ''
    if c_temps:
        clow = c_temps[0]
        chigh = c_temps[-1]
    data = {
        'wdates':wdates,
        'wtemps':wtemps,
        'wlow':wlow,
        'whigh':whigh,
        'cdates':cdates,
        'ctemps':ctemps,
        'clow':clow,
        'chigh':chigh
    }
    return render_template("graphs.html", **data)
@app.route('/onlygraphs')
def onlygraphs():
    #if not g.user and request.remote_addr != local_ip: return ('No access')
    wdata = sql_query("SELECT * FROM temps", True)
    wdates = [row[0] for row in wdata]
    wtemps = [row[1] for row in wdata]
    cdata = sql_query("SELECT * FROM ctemps", True)
    cdates = [row[0] for row in cdata]
    ctemps = [row[1] for row in cdata]
    data = {
        'wdates':wdates,
        'wtemps':wtemps,
        'cdates':cdates,
        'ctemps':ctemps
    }
    return render_template("onlygraphs.html", **data)
@app.route("/settimer", methods=["POST"])
def setLightTimer():
    """Provide a JSON object in your post request with keys
    `status` and `time`. Status being 'on' or 'off' and time being
    the time of day."""
    if request.method == "POST":
        msg = request.get_json(force=True)
        try: _time = time.strptime(msg['time'], '%H:%M')
        except ValueError: return ('Bad input')
        else:
            newTime = time.strftime('%H:%M', _time)
            if msg['status'] == "on":
                if leds.settings["onTime"] == newTime: return ('No change')
                elif leds.settings["offTime"] == newTime: return ('Duplicate times')
                leds.set_timer("on", newTime)
                status = f'On time set to {leds.settings["onTime"]}'
                return (f'{status}')
            elif msg['status'] == 'off':
                if leds.settings["offTime"] == newTime: return ('No change')
                elif leds.settings["onTime"] == newTime: return ('Duplicate times')
                leds.set_timer("off", newTime)
                status = f'Off time set to {leds.settings["offTime"]}'
                return (f'{status}')
@app.route('/index', methods=['POST','GET'])
def index():
    """This route mainly handles the LED strip controls
    with POST requests, it servers the main page as well.
    
    To toggle on/off, use {'ledtoggle':`'true'` or `'false'`}
    To change brightness, use {'brightness':`value`} Value being a percentage 0-100"""
    if request.method == 'POST':
        print(f"Toggle request received from {request.remote_addr}")
        if not request.remote_addr in IP_WHITELIST:
            if not g.user and request.remote_addr != local_ip: return (f'No access for {request.remote_addr}')
        else: print("Giving whitelisted IP a free pass ;)")
        theData = request.get_json(True)
        print(theData)
        if 'ledtoggle' in theData: leds.toggle(theData['ledtoggle'] == "true")
        if 'brightness' in theData: leds.set_brightness(theData['brightness'])
        return "Done"
    if not g.user and request.remote_addr != local_ip: return redirect(url_for('login'))
    #print(request.remote_addr)
    now = datetime.datetime.now()
    time = now.strftime("%B %d %Y %H:%M")
    if leds.enabled: ledstatus = "checked"
    else: ledstatus = ""
    if leds.rainbow:
        rainstat = 'niceText rainbow'
        color = "color:transparent;"
    else:
        rainstat = 'niceText'
        color = f"color:rgb({leds.color[0]},{leds.color[1]},{leds.color[2]});"
    data = {
        'time':time,
        'led':ledstatus,
        'brightness':str(leds.brightness * 100).replace('.0',''),
        'color':color,
        'col_r':leds.color[0],
        'col_g':leds.color[1],
        'col_b':leds.color[2],
        'rain':rainstat,
        'ontime':leds.settings["onTime"],
        'offtime':leds.settings["offTime"]
    }
    return render_template('main.html', **data)
@app.before_first_request
def rainbow_cycle():
    """An infinite while loop that makes the rainbow colors wave.
    Not used if the user selects a solid color."""
    def run_job():
        while True:
            if leds.enabled and leds.rainbow and rasp:
                leds.rainbow_cycle(0.03)
            else: time.sleep(5)
    thread = threading.Thread(target=run_job)
    thread.start()
if __name__ in ['__main__', 'main']:
    if rasp:
        print("Making sure LEDs are off")
        leds.enabled = False
        leds.pix.fill((0,0,0))
        leds.pix.show()
if __name__ == '__main__':
    try:
        app.run(debug=True,host='0.0.0.0', use_reloader=False)
        if rasp:
            print("Making sure LEDs are off")
            leds.enabled = False
            leds.pix.fill((0,0,0))
            leds.pix.show()
    except Exception as e: print(e)
    finally:
        if rasp:
            leds.enabled = False
            leds.pix.fill((0,0,0))
            leds.pix.show()
        exit()