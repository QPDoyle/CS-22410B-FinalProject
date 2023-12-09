import os
from abc import ABC, abstractmethod
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import smbus
import time
import face_recognition
from gpiozero import Servo
GPIO.setwarnings(False)

class OutputModule(ABC):
    @abstractmethod
    def output(self, source, flag=None):
        pass

class ServoModule(OutputModule):

    def __init__(self, pin):
        self.pin = pin
        self.servo = Servo(pin)
    def output(self, source, flag=None):
        if source < -1 or source > 1:
            raise Exception("Servo value must be between -1 and +1")
        self.servo.value = source
    def min(self):
        self.servo.min()
    def mid(self):
        self.servo.mid()
    def max(self):
        self.servo.max()

servo_module = ServoModule(16)
while True:
	servo_module.output(1)
	time.sleep(1)
	servo_module.output(-1)
	time.sleep(1)
