from flask import Flask, render_template
import time
from threading import Thread
import os
import SmartSafeUtils as ssu
import shutil
import datetime
import RPi.GPIO as GPIO

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    imgs = os.listdir('static/imgs')
    imgs = ['imgs/' + file for file in imgs]
    return render_template("index.html", title="SmartSafe invalid attempts", imgs = imgs)

def smart_safe_runner():
    lcd = ssu.LedModule()
    GPIO.setmode(GPIO.BCM)
    keypad = ssu.KeypadModule()
    rfid = ssu.RfidModule()
    camera = ssu.CameraModule()
    speaker = ssu.SpeakerModule()
    servo = ssu.ServoModule("16")
    while True:
        smart_safe(lcd, keypad, rfid, camera,speaker, servo)

def smart_safe(lcd, keypad, rfid, camera,speaker, servo):



    ##set servo to unlocked
    servo.output(-1)
    time.sleep(0.5)
    lcd.output("SmartSafe: Press", 1)
    lcd.output("ENTER to setup", 2)
    input()
    lcd.output("Input 4 digit", 1)
    lcd.output("PIN code..", 2)
    global valid_pin
    valid_pin = False

    while not valid_pin:
        valid_pin = keypad.set_password()
        if not valid_pin:
            lcd.output("Invalid format", 1)
            lcd.output("Input PIN again", 2)

    lcd.output("PIN code saved!", 1)
    lcd.output("", 2)
    time.sleep(1)

    lcd.output("Tap RFID key", 1)
    lcd.output("tag", 2)
    rfid.set_password()
    lcd.output("RFID tag saved!", 1)
    lcd.output("", 2)

    lcd.output("Face recognition", 1)
    lcd.output("Press ENTER", 2)
    input()
    global valid_photo
    valid_photo = False
    while not valid_photo:
        lcd.output("Look directly into", 1)
        lcd.output("camera,dont move", 2)
        time.sleep(2)
        valid_photo = camera.set_password()
        if not valid_photo:
            lcd.output("Face not found", 1)
            lcd.output("ENTER to retake", 2)
            input()
    lcd.output("Face saved!", 1)
    lcd.output("Press ENTER", 2)
    input()

    lcd.output("Ready to lock?", 1)
    lcd.output("Press ENTER", 2)
    input()
    ## lock servo
    while True:
        servo.output(1)
        time.sleep(1)
        lcd.output("Safe locked", 1)
        lcd.output("Press ENTER", 2)

        lcd.output("Input 4 digit", 1)
        lcd.output("PIN code..", 2)
        valid_pin = False
        while not valid_pin:
            valid_pin = keypad.set_answer()
            if not valid_pin:
                lcd.output("Invalid format", 1)
                lcd.output("Input PIN again", 2)

        if not keypad.validate_password():
              lcd.output("Invalid password", 1)
              lcd.output("Access denied!", 2)
              speaker.output("LOUD.mp3")
              time.sleep(4)
              valid_photo = False
              valid_pin = False
              continue

        lcd.output("PIN verified!", 1)
        lcd.output("Press ENTER", 2)
        speaker.output("CHECK.mp3")
        input()

        lcd.output("Tap RFID key", 1)
        lcd.output("tag", 2)
        rfid.set_answer()
        if not rfid.validate_password():
              lcd.output("Invalid RFID", 1)
              lcd.output("Access denied!", 2)
              speaker.output("LOUD.mp3")
              time.sleep(4)
              valid_photo = False
              valid_pin = False
              continue
        lcd.output("RFID verified!", 1)
        speaker.output("CHECK.mp3")
        lcd.output("Press ENTER", 2)
        input()

        lcd.output("Face recognition", 1)
        lcd.output("Press ENTER", 2)
        input()
        valid_photo = False
        while not valid_photo:
            lcd.output("Look directly into", 1)
            lcd.output("camera,dont move", 2)
            time.sleep(2)
            valid_photo = camera.set_answer()
            if not valid_photo:
                lcd.output("Face not found", 1)
                lcd.output("ENTER to retake", 2)
                input()
        if not camera.validate_password():
            lcd.output("Invalid face", 1)
            lcd.output("Access denied!", 2)
            speaker.output("LOUD.mp3")
            src_dir = "image_password_unknown.jpg"
            timestamp = str(datetime.datetime.now())[:19]
            timestamp = timestamp.replace(":", "-")
            dst_dir = "static/imgs/" + str(timestamp) + ".jpg";
            shutil.copy(src_dir, dst_dir)
            time.sleep(4)
            valid_photo = False
            valid_pin = False
            continue
        lcd.output("Face verified!", 1)
        speaker.output("CHECK.mp3")
        lcd.output("Press ENTER", 2)
        input()
        lcd.output("Identity verifi-", 1)
        lcd.output("ed, UNLOCKING", 2)
        time.sleep(2)
        ##unlock servo
        servo.output(-1)
        time.sleep(1)
        lcd.output("SmartSafe", 1)
        lcd.output("UNLOCKED", 2)
        speaker.output("CHECK.mp3")
        break

smart_safe_runner_thread = Thread(target=smart_safe_runner)
smart_safe_runner_thread.start()
