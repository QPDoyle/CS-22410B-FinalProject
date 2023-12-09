import SmartSafeUtils as ssu
import time

print("\n \n \n \n SmartSafe \n")

lcd = ssu.LedModule()
lcd.output("SmartSafe",1)
lcd.output("Insert PIN", 2)
"""
keypad = ssu.KeypadModule()
if keypad.set_password():
	if not keypad.set_answer():
		lcd.output("Invalid format", 2)
		time.sleep(2)
		exit()
	if keypad.validate_password():
		print("Password matches - welcome!")
		lcd.output("PIN verified", 2)
		time.sleep(2)
	else:
		print("Incorrect password")
		lcd.output("PIN invalid", 2)
		time.sleep(2)
		exit()
else:
	print("Invalid password format!")
	lcd.output("Invalid format", 2)
	time.sleep(2)
	exit()
print("\n")


"""
print("\n")

rfid = ssu.RfidModule()
lcd.output("Insert key",2)
rfid.set_password()
time.sleep(1)
lcd.output("Verify key",2)
rfid.set_answer()
time.sleep(1)
if not rfid.validate_password():
	exit()
time.sleep(1)

camera = ssu.CameraModule()
speaker = ssu.SpeakerModule()
lcd.output("Scan face",2)
input("Press any key...")
camera.set_password()
input("Press any key...")
lcd.output("Verify face",2)
camera.set_answer()
if camera.validate_password():
	lcd.output("FACES MATCH", 2)
	print("FACES MATCH")
	speaker.output("success.mp3")
else:
	lcd.output("NO MATCH", 2)
	print("NO MATCH")
	speaker.output("error.wav")
time.sleep(5)
