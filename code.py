import time
import board
import RPi.GPIO as GPIO
from adafruit_tcs34725 import TCS34725
import busio
import subprocess

TRIG = 17 #GPIO17
ECHO = 18 #GPIPO18
BtnPin = 5 #GPIO 5
VibPin = 26 #GPI0 26
s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

def speak(text):
	subprocess.run(["espeak", text])

def setup(): 
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(VibPin, GPIO.OUT)
	GPIO.setup(signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(s2, GPIO.OUT)
	GPIO.setup(s3, GPIO.OUT)
	print("\n")
	GPIO.setwarnings(False)
	# GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=detect, bouncetime=200)

def freq_to_rgb(value, min_freq, max_freq):
	temporary = (value - min_freq) * 255 / (max_freq - min_freq)
	normalized = min(max(0, temporary), 255)
	return normalized
	
def detect(chn):
		global buttonState
		buttonState = not buttonState
		print("button state: ", buttonState)
		
	
def distance():
	GPIO.output(TRIG, 0)
	time.sleep(0.000002)

	GPIO.output(TRIG, 1)
	time.sleep(0.00001)
	GPIO.output(TRIG, 0)

	
	while GPIO.input(ECHO) == 0:
		a = 0
	time1 = time.time()
	while GPIO.input(ECHO) == 1:
		a = 1
	time2 = time.time()

	during = time2 - time1
	return during * 340 / 2 * 100
		

def get_color():
	r, g, b, _ = sensor.color_rgb_bytes
	return r, g, b
	
def get_color_name(rgb):
	r, g, b = rgb
	if r > 200 and g > 200 and b > 200:
		return 'white'
	elif r < 100 and g < 100 and b < 100:
		return 'black'
	elif r > b and r > g:
		return 'red'
	elif g > r and g > b:
		return 'green'
	else:
		return 'blue'

def output_color():
	min_freq = 10000  # Example minimum frequency (should be calibrated)
	max_freq = 50000  # Example maximum frequency (should be calibrated)
	
	GPIO.output(s2, GPIO.LOW)
	GPIO.output(s3, GPIO.LOW)
	time.sleep(0.3)
	start = time.time()
	for impulse_count in range(NUM_CYCLES):
		GPIO.wait_for_edge(signal, GPIO.FALLING)
	duration = time.time() - start
	red_freq = NUM_CYCLES / duration
	red = freq_to_rgb(red_freq, min_freq, max_freq)

	GPIO.output(s2, GPIO.LOW)
	GPIO.output(s3, GPIO.HIGH)
	time.sleep(0.3)
	start = time.time()
	for impulse_count in range(NUM_CYCLES):
		GPIO.wait_for_edge(signal, GPIO.FALLING)
	duration = time.time() - start
	blue_freq = NUM_CYCLES / duration
	blue = freq_to_rgb(blue_freq, min_freq, max_freq)

	GPIO.output(s2, GPIO.HIGH)
	GPIO.output(s3, GPIO.HIGH)
	time.sleep(0.3)
	start = time.time()
	for impulse_count in range(NUM_CYCLES):
		GPIO.wait_for_edge(signal, GPIO.FALLING)
	duration = time.time() - start
	green_freq = NUM_CYCLES / duration
	green = freq_to_rgb(green_freq, min_freq, max_freq)

	color_name = get_color_name((red, green, blue))
	print(color_name)
	speak(f"The color is {color_name}")
	time.sleep(2)


def detect_object():
	button_state = False
	while True:
		if GPIO.input(BtnPin) == GPIO.LOW:
			button_state = True
			print("Button is ON")
			speak(f"The glove is on")
			time.sleep(0.2)
			while (button_state):
				dist = distance()
				if dist < 20:
					output_color()
				else: 
					GPIO.output(VibPin, GPIO.HIGH)
					time.sleep(0.5)
					GPIO.output(VibPin, GPIO.LOW)
				if GPIO.input(BtnPin) == GPIO.LOW:
					button_state = False
					print("Button is OFF")
					speak(f"The glove is off")
					break
			
def endprogram():
	GPIO.cleanup()

if __name__ == '__main__' :
	setup()
	try:
		detect_object()
	except KeyboardInterrupt:
		endprogram()
