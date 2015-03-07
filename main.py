import RPi.GPIO as GPIO
import time
import math
from datetime import datetime


MULTIPLIER = 171.5
WAITTIME = 0.0
MAX_DIFFERENCE = 0.2

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
    with open(LOGFILE, "w+") as f:
        f.write("[" + str(datetime.now()) + "] " + ERR_TEXT[errlvl] + text + '\n')


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

    print("distance[" + str(i) + "] = " + str(distance) + " m")


def clear_wdata(i):
    for n in range(len(WDATA[i])):
        WDATA[i][n] = 0


def save_result(i):
    DATA[i].append(RESULT[i][0])
    TIME[i].append(RESULT[i][1])
    clear_wdata(i)
    print_result(i)


def check_all_results():
    for i in range(len(RESULT)):
        check_results(i)


def check_results(i):
    global velocity
    if len(DATA[i]) >= 1 and RESULT[i][0] > 0:
        n = DATA[i][len(DATA[i]) - 1]
        l = len(DATA[i])

        if math.fabs(RESULT[i][0] - n) > timeFromDistance(MAX_DIFFERENCE):
            if WDATA[i][0] == 0:
                WDATA[i][0] = RESULT[i][0]
            elif WDATA[i][1] == 0:
                WDATA[i][1] = RESULT[i][0]
            else:
                if math.fabs(n - WDATA[i][0]) < timeFromDistance(MAX_DIFFERENCE) and math.fabs(n - WDATA[i][1]) < timeFromDistance(MAX_DIFFERENCE):
                    save_result(i)
                clear_wdata(i)
            if not len(DATA[i]) > l:  #if value has not been saved in DATA
                log("deviant measurement[" + str(i) + "] = " + str(RESULT[i][0] * MULTIPLIER) + " m", 2)
        else:
            save_result(i)

        if len(DATA[i]) >= 2:
            velocity = (MULTIPLIER * (DATA[i][len(DATA[i]) - 2] - DATA[i][len(DATA[i]) - 1]) /
                    float(TIME[i][len(TIME[i]) - 2] - TIME[i][len(TIME[i]) - 1]))
    elif RESULT[i][0] > 0:
        save_result(i)
    else:
        log("wrong measurement[" + str(i) + "] = " + str(RESULT[i][0] * MULTIPLIER) + " m", 2)


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
    global velocity

    angle = (a) / float(180) * 3.141592653
    #radius = 61
    radius = 105
    line = (radius * angle) / float(100)

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


def drive1():
    log("started program main.py with function drive1()", 0)

    t = float(input("brake_time: "))
    log("set parameter t = " + str(t), 0)
    d = float(input("distance: "))
    log("set parameter d = " + str(d), 0)
    countdown(8)
    log("started driving", 0)

    driveForward()
    measure(0)
    check_results(0)
    log("first measurement[0] = " + str(DATA[0][len(DATA) - 1] * MULTIPLIER) + " m", 1)
    while DATA[0][len(DATA) - 1] > timeFromDistance(d):  #while distance is larger than d
        measure(0)
        check_results(0)
    log("measurement[0] = " + str(DATA[0][len(DATA) - 1] * MULTIPLIER) + " < d", 0)
    brake(t)
    log("stopped function drive1()", 0)


def drive2():
    driveForward()
    start = time.time()
    measure(0)
    check_results(0)
    while (time.time() - start) < 1:  #for 1s
        measure(0)
        check_results(0)
    turn(90)
    stopdrive()


def drive3(angle):
    driveForward()
    measure(0)
    check_results(0)
    while RESULT[0][0] > timeFromDistance(150):  #while distance is larger than 150 cm
        measure(0)
        check_results(0)
    turn(angle)
    measure(0)
    check_results(0)
    while RESULT[0][0] > timeFromDistance(64):  #while distance is larger than 64 cm
        measure(0)
        check_results(0)
    brake(0.5)


setup()

#angle = int(raw_input("angle: "))
drive1()

log("stopped program main.py", 0)
