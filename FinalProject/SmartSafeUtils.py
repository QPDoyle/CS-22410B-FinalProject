import os
from abc import ABC, abstractmethod
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import smbus
import time
import face_recognition
from picamera import PiCamera
from gpiozero import Servo
import pygame
GPIO.setwarnings(False)


class OutputModule(ABC):
    @abstractmethod
    def output(self, source, flag=None):
        pass


class SecurityModule(ABC):
    @abstractmethod
    def set_password(self):
        pass

    @abstractmethod
    def set_answer(self):
        pass

    @abstractmethod
    def validate_password(self):
        pass


class RfidModule(SecurityModule):

    def __init__(self):
        self.__password = None
        self.__answer = None
        self.reader = SimpleMFRC522()

    def set_password(self):
        password = self.read_data()
        self.__password = password[0]
        print("RFID code saved: " + str(self.__password))
        return True

    def set_answer(self):
        answer = self.read_data()
        self.__answer = answer[0]
        print("RFID code saved: " + str(self.__password))
        return True

    def validate_password(self):
        if self.__password == None or self.__answer == None:
            raise Exception("Password and answer must be set before validating!")
        if (self.__answer == self.__password):
            print("RFID code validated: " + str(self.__password))
            return True
        print("Invalid RFID " + str(self.__answer) + " != " + str(self.__password))
        return False

    def read_data(self):
        try:
            print("Insert RFID tag to be read")
            rfid_id, rfid_text = self.reader.read()
            return rfid_id, rfid_text
        except:
            raise Exception("And error has occurred while reading RFID data!")

    def write_data(self, text):
        try:
            print("Insert RFID tag to be overwritten")
            self.reader.write(text)
            print("Data \"" + text + "\" was saved on RFID")
        except:
            raise Exception("And error has occurred while writing RFID data!")


class KeypadModule(SecurityModule):

    def __init__(self):
        self.__password = None
        self.__answer = None

    def set_password(self):
        password = input("Enter 4 digit PIN code please: ")
        if len(password) == 4 and password.isdigit():
            self.__password = password
            return True
        return False

    def set_answer(self):
        answer = input("Enter 4 digit PIN code please: ")
        if len(answer) == 4 and answer.isdigit():
            self.__answer = answer
            return True
        return False

    def validate_password(self):
        if self.__answer == self.__password:
            return True
        return False


class LedModule(OutputModule):
    # Define some device parameters
    I2C_ADDR = 0x27  # I2C device address
    LCD_WIDTH = 16  # Maximum characters per line
    # Define some device constants
    LCD_CHR = 1  # Mode - Sending data
    LCD_CMD = 0  # Mode - Sending command

    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

    LCD_BACKLIGHT = 0x08  # On
    ENABLE = 0b00000100  # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    # Open I2C interface


    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.lcd_init()
        self.output(" ",1)
        self.output(" ",2)


    def __del__(self):
        self.lcd_byte(0x01, self.LCD_CMD)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command

        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT

        # High bits
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        # Low bits
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_init(self):
        # Initialise display
        self.lcd_byte(0x33, self.LCD_CMD)  # 110011 Initialise
        self.lcd_byte(0x32, self.LCD_CMD)  # 110010 Initialise
        self.lcd_byte(0x06, self.LCD_CMD)  # 000110 Cursor move direction
        self.lcd_byte(0x0C, self.LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28, self.LCD_CMD)  # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, self.LCD_CMD)  # 000001 Clear display
        time.sleep(self.E_DELAY)

    def lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR, (bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def output(self, source, flag=None):
        if flag == 1:
            line = self.LCD_LINE_1
        elif flag == 2:
            line = self.LCD_LINE_2
        else:
            print(source)
            print(flag)
            return False
        message = source.ljust(self.LCD_WIDTH, " ")

        self.lcd_byte(line, self.LCD_CMD)

        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)

        time.sleep(0.1)
        return True


class CameraModule(SecurityModule):
    def __init__(self):
        self.camera = PiCamera()
    def set_password(self):
        self.camera.start_preview()
        print("Taking a photo, please stay still and look at the camera..")
        time.sleep(0.5)
        self.camera.capture('image_password_known.jpg')
        self.camera.stop_preview()
        try:
            known_image = face_recognition.load_image_file("image_password_known.jpg")
            known_encoding = face_recognition.face_encodings(known_image)[0]
        except:
            print("Face not found in the photo")
            return False
        print("Face scanning finished")
        return True

    def set_password_from_file(self, fileName):
        if not fileName.lower().endswith(('.jpg', '.jpeg')):
            return False
        os.rename(fileName, 'image_password_known.jpg')
        try:
            known_image = face_recognition.load_image_file("image_password_known.jpg")
            known_encoding = face_recognition.face_encodings(known_image)[0]

        except:
            print("Face not found in the photo")
            return False
        return True

    def set_answer(self):
        self.camera.start_preview()
        print("Taking a photo, please stay still and look at the camera..")
        time.sleep(0.5)
        self.camera.capture('image_password_unknown.jpg')
        self.camera.stop_preview()
        try:
            unknown_image = face_recognition.load_image_file("image_password_unknown.jpg")
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        except:
            print("Face not found in the photo")
            return False
        print("Face scanning finished")
        return True
    def validate_password(self):
        try:
            known_image = face_recognition.load_image_file("image_password_known.jpg")
            unknown_image = face_recognition.load_image_file("image_password_unknown.jpg")
            print("Validating your facial features, please wait...")
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        except:
            raise Exception("An issue occurred while analyzing the images!")
        results = face_recognition.compare_faces([known_encoding], unknown_encoding)
        return results[0]

class SpeakerModule(OutputModule):

    def __init__(self):
        pygame.mixer.init()
    def output(self, source, flag=None):
        pygame.mixer.music.load(source)
        pygame.mixer.music.play()

class ServoModule(OutputModule):

    def __init__(self, pin):
        self.pin = pin
        self.servo = Servo(pin)
    def output(self, source, flag=None):
        if source < -1 or source > 1:
            raise Exception("Servo value must be between -1 and +1!")
        self.servo.value = source
    def min(self):
        self.servo.min()
    def mid(self):
        self.servo.mid()
    def max(self):
        self.servo.max()
