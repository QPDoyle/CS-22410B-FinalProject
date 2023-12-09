import SmartSafeUtils as ssu

camera = ssu.CameraModule()
input("Press Enter to continue...")
camera.set_password()
input("Press Enter to continue...")
res = camera.validate_password()
print(res)
if res == True:
	print("Faces match! Welcome!")
else:
	print("Faces dont match!")
