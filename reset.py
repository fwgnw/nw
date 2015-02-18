import RPi.GPIO as GPIO

TRIG = [29, 31, 32, 33]

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

for trig in TRIG:
  GPIO.setup(trig, GPIO.OUT)
  GPIO.output(trig, False)
