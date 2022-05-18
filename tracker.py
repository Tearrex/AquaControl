import random, os, time, sqlite3, datetime, platform, subprocess, glob, sys

def sql_query(query:str, result:bool=False, commit:bool=False, param=None, db='temperatures.db'):
    #if platform.system() == "Linux":
        #conn = sqlite3.connect(f"/home/pi/git/projects/AquaControl/{db}")
    #else: conn = sqlite3.connect(db)
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    if not param: cursor.execute(query)
    else: cursor.execute(query, param)
    results = None
    if result: results = cursor.fetchall()
    elif commit: conn.commit()
    conn.close()
    return results

def fake_temp(): return random.randint(70,80)

def prime():
    if platform.system() == "Linux":
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        device_file = device_folder + '/w1_slave'

def read_raw():
    with open(device_file, 'r') as t: lines = t.readlines()
    return lines
def read_temp():
    """Reads the temperature probe's current temperature.
    It will return the fahrenheit and celcius measurements, respectively."""
    lines = read_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0 #celcius for CPU
        temp_f = temp_c * 9.0 / 5.0 + 32.0 #fahrenheit for water
        return round(temp_c,1), round(temp_f,1)
def get_all_temps():
    """Returns a tuple that corresponds to the water and CPU temperatures."""
    ctemp = str(subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp']))
    ctemp = ctemp.split('=')[1].split('\\n')[0].split("'")[0]
    wtemp = read_temp()[1]
    return (wtemp, float(ctemp))

# Handles the polling task of the script. Set your desired poll rate
# as a command line argument. It should be an amount of time in seconds.
#
# I have it setup to run on boot with my rc.local file:
# python3 /home/pi/git/projects/AquaControl/tracker.py 900 &
#
# Now it will record the water and CPU temperatures every 15 minutes!
# Don't forget the & symbol as this script executes an infinite loop.
if __name__ == '__main__':
    prime() # prime the temperature probe to read its data
    if platform.system() == "Windows":
        table = ""
        while table == "":
            temp = input("What table?\n[1] Water Temp\n[2] CPU Temp\n")
            if temp == "1": table = "temps"
            elif temp == "2": table = "ctemps"
        current = low = high = fake_temp()
        while True:
            current = fake_temp()
            if current > high: high = current
            elif current < low: low = current
            _now = datetime.datetime.now()
            _time = _now.strftime("%m-%d-%Y %H:%M")
            try: sql_query(f"INSERT INTO {table} VALUES (?, ?)", False, True, (_time, current))
            except Exception as e: print(f"Query error: {e}")
            print(f"Now: {current} Low: {low} High: {high}")
            time.sleep(10)
    else:
        pollRate = None
        if len(sys.argv) == 2:
            try: pollRate = int(sys.argv[1])
            except ValueError: pass
        while not pollRate:
            temp = input("Set polling rate (in seconds): ")
            try: temp = float(temp)
            except ValueError: pass
            else: pollRate = temp
        tables = ["temps", "ctemps"]
        while True:
            temps = get_all_temps()
            _now = datetime.datetime.now()
            _time = _now.strftime("%m-%d-%y %H:%M").lstrip('0')
            for i, t in enumerate(temps):
                try: sql_query(f"INSERT INTO {tables[i]} VALUES (?, ?)", False, True, (_time, t))
                except Exception as e: print(f"Query error: {e}")
            os.system('clear')
            print(f"Water: {temps[0]}F CPU: {temps[1]}C")
            time.sleep(pollRate)