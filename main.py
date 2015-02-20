import RPi.GPIO as GPIO
import time
import math
from datetime import datetime


MULTIPLIER = 17150
WAITTIME = 0.0
MAX_DIFFERENCE = 20

TRIG = [16, 38, 35, 13]
ECHO = [18, 36, 37, 11]
RESULT = [[0, 0], [0, 0], [0, 0], [0, 0]]
DATA = [[], [], [], []]  #0: front, 1: left, 2: back, 3: right
TIME = [[], [], [], []]
WDATA = [[0, 0], [0, 0], [0, 0], [0, 0]]

MOTOR = [29, 31, 32, 33]  #0: engine+, 1: engine-, 2: steering+, 3: steering-

LOGFILE = "main.log"
ERR_TEXT = ["", "INF: ", "ERR: "]

drivingForward = False
drivingBackward = False

measurements = 0
successful_measurements = [0, 0, 0, 0]

timeOfLastMeasurement = 0
velocity = 0


def setup():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    for trig in TRIG:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.output(trig, False)

    for echo in ECHO:
        GPIO.setup(echo, GPIO.IN)

    for motor in MOTOR:
        GPIO.setup(motor, GPIO.OUT)
        GPIO.output(motor, False)


def log(text, errlvl):
    with open(LOGFILE, "a+") as f:
        f.write("[" + datetime.now() + "] " + ERR_TEXT[errlvl] + text)


def measure(i):
    GPIO.output(TRIG[i], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[i], False)

    msr_start = time.time()

    pulse_start = -1
    pulse_end = 0

    while GPIO.input(ECHO[i]) == 0:
        pulse_start = time.time()
        if time.time() - msr_start > 0.025:
            break

    while GPIO.input(ECHO[i]) == 1:
        pulse_end = time.time()
        if time.time() - msr_start > 0.025:
            break

    if time.time() - msr_start > 0.025:
        RESULT[i][0] = -1
        RESULT[i][1] = pulse_end
    else:
        RESULT[i][0] = pulse_end - pulse_start
        RESULT[i][1] = pulse_end

    time.sleep(WAITTIME)


def print_result(i):
    distance = RESULT[i][0] * MULTIPLIER
    distance = round(distance, 2)

    print("distance[" + str(i) + "] = " + str(distance) + " cm")


def clear_wdata(i):
    for n in range(len(WDATA[i])):
        WDATA[i][n] = 0


def save_result(i):
    DATA[i].append(RESULT[i][0])
    TIME[i].append(RESULT[i][1])
    clear_wdata(i)
    successful_measurements[i] += 1
    print_result(i)


def check_results():
    global timeOfLastMeasurement, velocity
    for i in range(len(RESULT)):
        if len(DATA[i]) >= 1 and RESULT[i][0] > 0:
            n = DATA[i][len(DATA[i]) - 1]

            if math.fabs(RESULT[i][0] - n) > timeFromDistance(MAX_DIFFERENCE):
                if WDATA[i][0] == 0:
                    WDATA[i][0] = n
                elif WDATA[i][1] == 0:
                    WDATA[i][1] = n
                else:
                    if math.fabs(n - WDATA[i][0]) < timeFromDistance(MAX_DIFFERENCE):
                        if math.fabs(n - WDATA[i][1]) < timeFromDistance(MAX_DIFFERENCE):
                            save_result(i)
                    clear_wdata(i)
            else:
                save_result(i)

            if len(DATA[i]) >= 2:
                velocity = ((MULTIPLIER * DATA[i][len(DATA[i]) - 2] - MULTIPLIER * DATA[i][len(DATA[i]) - 1]) / float(100)) / float(time.time() - timeOfLastMeasurement)

            timeOfLastMeasurement = time.time()
        elif RESULT[i][0] > 0:
            save_result(i)
        else:
            log("wrong measurement[" + len(DATA[i]) - 1 + "] = " + RESULT[i][0] * MULTIPLIER, 2)


def timeFromDistance(distance):
    return distance / float(MULTIPLIER)


def driveForward():
    global drivingForward
    global drivingBackward
    GPIO.output(MOTOR[0], True)
    drivingForward = True
    GPIO.output(MOTOR[1], False)
    drivingBackward = False

def driveBackward():
    global drivingForward
    global drivingBackward
    GPIO.output(MOTOR[0], False)
    drivingForward = False
    GPIO.output(MOTOR[1], True)
    drivingBackward = True

def stopdrive():
    global drivingForward
    global drivingBackward
    GPIO.output(MOTOR[0], False)
    drivingForward = False
    GPIO.output(MOTOR[1], False)
    drivingBackward = False

def steerLeft():
    GPIO.output(MOTOR[2], False)
    GPIO.output(MOTOR[3], True)

def steerRight():
    GPIO.output(MOTOR[2], True)
    GPIO.output(MOTOR[3], False)

def stopsteer():
    GPIO.output(MOTOR[2], False)
    GPIO.output(MOTOR[3], False)


def brake(t):
    log("started braking", 0)
    BRAKETIME = t
    if drivingForward:
        print("driving BACKWARD")
        driveBackward()
        time.sleep(BRAKETIME)
    elif drivingBackward:
        print("driving FORWARD")
        driveForward()
        time.sleep(BRAKETIME)
    stopdrive()
    log("stopped braking", 0)


def turn(a):
    global timeOfLastMeasurement, velocity
    i = 0
    if len(DATA[i]) >= 2:
        open(LOGFILE, "a+").write(str(MULTIPLIER * DATA[i][len(DATA[i]) - 2]) + " cm - " + str(MULTIPLIER * DATA[i][len(DATA[i]) - 1]) + " cm\n")
        open(LOGFILE, "a+").write(str(float(time.time() - timeOfLastMeasurement)) + " s\n")
        open(LOGFILE, "a+").write("velocity: " + str(velocity) + "\n")

    angle = (a) / float(180) * 3.141592653
    #radius = 61
    radius = 105
    line = (radius * angle) / float(100)

    open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] velocity: " + str(velocity) + " m/s\n")
    if velocity != 0:
        open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] time for turn: " + str(line / float(velocity)) + " s\n")
    else :
        open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] time for turn: ERROR velocity=0\n")

    if velocity > 0:
        steerLeft()
        time.sleep(line / float(velocity))
        stopsteer()


def countdown(t):
    log("started countdown(" + str(t) + ")", 0)
    for i in range(t):
        print(t - i)
        time.sleep(1)
    log("stopped countdown", 0)


def drive1(t, d):
    log("started program main.py with function drive1()", 0)

    t = float(input("brake_time: "))
    log("set parameter t = " + str(t), 0)
    d = float(input("distance: "))
    log("set parameter d = " + str(d), 0)
    countdown(8)
    log("started driving", 0)

    driveForward()
    measure(0)
    check_results()
    log("first measurement[0] = " + str(RESULT[0][0] * MULTIPLIER), 1)
    while RESULT[0][0] > timeFromDistance(d):  #while distance is larger than d
        measure(0)
        check_results()
    log("measurement[0] = " + str(RESULT[0][0] * MULTIPLIER) + " < ", 0)
    brake(t)
    log("stopped function drive1()", 0)


def drive2():
    driveForward()
    start = time.time()
    measure(0)
    check_results()
    while (time.time() - start) < 1:  #for 1s
        measure(0)
        check_results()
    turn()
    stopdrive()


def drive3(angle):
    driveForward()
    measure(0)
    check_results()
    while RESULT[0][0] > timeFromDistance(150):  #while distance is larger than 150 cm
        measure(0)
        check_results()
    turn(angle)
    measure(0)
    check_results()
    while RESULT[0][0] > timeFromDistance(64):  #while distance is larger than 64 cm
        measure(0)
        check_results()
    brake()


setup()

#angle = int(raw_input("angle: "))
drive1(t, d)

log("stopped program main.py")
