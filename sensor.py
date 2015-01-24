import RPi.GPIO as GPIO
import time
import math


MULTIPLIER = 17150
WAITTIME = 0.125

TRIG = [16, 38, 35, 13]
ECHO = [18, 36, 37, 11]
RESULT = [0, 0, 0, 0]
DATA = [[], [], [], []]  #0: front, 1: left, 2: back, 3: right
WDATA = [[0, 0], [0, 0], [0, 0], [0, 0]]

MOTOR = [32, 33, 31, 29]  #0: engine+, 1: engine-, 2: steering+, 3: steering-

LOGFILE = "log/" + str(int(time.time())) + ".log"

measurements = 0
successful_measurements = [0, 0, 0, 0]


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


def measure(i):
    GPIO.output(TRIG[i], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[i], False)

    msr_start = time.time()

    pulse_start = -1
    pulse_end = 0

    while GPIO.input(ECHO[i]) == 0:
        pulse_start = time.time()
        if time.time() - msr_start > 0.05:
            break

    while GPIO.input(ECHO[i]) == 1:
        pulse_end = time.time()
        if time.time() - msr_start > 0.05:
            break

    if time.time() - msr_start > 0.05:
        RESULT[i] = -1
    else:
        RESULT[i] = pulse_end - pulse_start

    time.sleep(WAITTIME)


def print_result(i):
    distance = RESULT[i] * MULTIPLIER
    distance = round(distance, 2)

    print("distance[" + str(i) + "] = " + str(distance) + " cm")


def clear_wdata(i):
    for n in range(len(WDATA[i])):
        WDATA[i][n] = 0


def save_result(i, file):
    DATA[i].append(RESULT[i])
    file.write(str(round(RESULT[i] * MULTIPLIER, 2)) + "\n")
    clear_wdata(i)
    successful_measurements[i] += 1
    print_result(i)


def check_results():
    with open(LOGFILE, "a+") as file:
        for i in range(len(RESULT)):
            if len(DATA[i]) >= 1 and RESULT[i] > 0:
                n = DATA[i][len(DATA[i]) - 1]

                if math.fabs(RESULT[i] - n) > math.fabs(n) / 100.0 * 10:
                    if WDATA[i][0] == 0:
                        WDATA[i][0] = n
                    elif WDATA[i][1] == 0:
                        WDATA[i][1] = n
                    else:
                        if math.fabs(n - WDATA[i][0]) < math.fabs(WDATA[i][0]) / 100.0 * 10:
                            if math.fabs(n - WDATA[i][1]) < math.fabs(WDATA[i][1]) / 100.0 * 10:
                                save_result(i, file)
                            else:
                                clear_wdata(i)
                        else:
                            clear_wdata(i)
                else:
                    save_result(i, file)
            elif RESULT[i] > 0:
                save_result(i, file)
                file.write("\n")


def timeFromDistance(distance):
    return distance / float(MULTIPLIER)


def testdrive():
    GPIO.output(MOTOR[0], True)
    time.sleep(10)
    GPIO.output(MOTOR[0], False)

def driveForward():
    GPIO.output(MOTOR[0], True)
    GPIO.output(MOTOR[1], False)

def driveBackward():
    GPIO.output(MOTOR[0], False)
    GPIO.output(MOTOR[1], True)

def stopdrive():
    GPIO.output(MOTOR[0], False)
    GPIO.output(MOTOR[1], False)

def steerLeft():
    GPIO.output(MOTOR[2], False)
    GPIO.output(MOTOR[3], True)

def steerRight():
    GPIO.output(MOTOR[2], True)
    GPIO.output(MOTOR[3], False)

def stopsteer():
    GPIO.output(MOTOR[2], False)
    GPIO.output(MOTOR[3], False)


def steertest():
    while True:
        measure(0)
        check_results()

        if RESULT[0] < timeFromDistance(50):
            steerLeft()
        else:
            stopsteer()


def drive1():
    time.sleep(15)
    driveForward()
    measure(0)
    check_results()
    while RESULT[0] > timeFromDistance(100):  #while distance is larger than 1m
        measure(0)
        check_results()
    '''
    driveBackward()
    time.sleep(2)
    '''
    stopdrive()


def drive2():
    time.sleep(15)
    driveForward()
    time.sleep(1)
    stopdrive()


MULTIPLIER = int(input("M = "))

setup()

for glhf in range(100):
    prgrm_start = time.time()

    for i in range(len(TRIG)):
        measure(i)
        check_results()
        measurements += 1

    prgrm_end = time.time()
    print("duration = " + str(round(prgrm_end - prgrm_start, 2)) + " s")

GPIO.cleanup()

print(measurements)
print("0: " + str(round(successful_measurements[0] / float(measurements) * 100, 2)))
print("1: " + str(round(successful_measurements[1] / float(measurements) * 100, 2)))
print("2: " + str(round(successful_measurements[2] / float(measurements) * 100, 2)))
print("3: " + str(round(successful_measurements[3] / float(measurements) * 100, 2)))
