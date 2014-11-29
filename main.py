import RPi.GPIO as GPIO
import time


MULTIPLIER = 17150

TRIG = [16, 38, 35, 13]
ECHO = [18, 36, 37, 11]
RESULT = [0, 0, 0, 0]
DATA = [[], [], [], []]

LOGFILE = "log/" + str(int(time.time())) + ".log"


def setup():
    GPIO.cleanup()

    GPIO.setmode(GPIO.BOARD)

    for trig in TRIG:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.output(trig, False)

    for echo in ECHO:
        GPIO.setup(echo, GPIO.IN)


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
    
    time.sleep(.25)


def print_result(i):
    distance = RESULT[i] * MULTIPLIER
    distance = round(distance, 2)

    print("distance[" + str(i) + "] = " + str(distance) + " cm")


def save_result(i):
	DATA[i].append(RESULT[i])
	file.write(str(round(RESULT[i] * MULTIPLIER, 2)) + "\n")


def save_results():
    with open(LOGFILE, "a+") as file:
        for i in range(len(RESULT)):
			if len(DATA) >= 1:
				if math.fabs(RESULT[i] - DATA[i]) > DATA[i] / 100.0 * 10:
					'''
					WRONG VALUE
					'''
				else:
					save_result(i)
			else:
				save_result(i)
        file.write("\n")


MULTIPLIER = int(input("M = "))

setup()

while True:
    prgrm_start = time.time()

    for i in range(len(TRIG)):
		measure(i)
		print_result(i)
    save_results()

    prgrm_end = time.time()
    print("duration = " + str(round(prgrm_end - prgrm_start, 2)) + " s")

GPIO.cleanup()