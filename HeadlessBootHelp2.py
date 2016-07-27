#!/usr/bin/python3

import sys

# Just sorting out the library references for the OLED.  Bit messy - could be cleaned up later
#sys.path.append('/usr/local/lib/python2.7/dist-packages/Adafruit_GPIO-1.0.0-py2.7.egg')
#sys.path.append('/usr/local/lib/python2.7/dist-packages/Adafruit_SSD1306-1.6.0-py2.7.egg')
#sys.path.append('/usr/local/lib/python2.7/dist-packages/Adafruit_PureIO-0.2.0-py2.7.egg')
import Adafruit_SSD1306
from subprocess import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import time
import re
 
 

# Runs a system command
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

# Prints out to the OLED screen.  ClearWidth and ClearHeight specify how much of screen to clear.  
# XLoc and YLic specify X/Y Coordinates of where to print the text. 	
def OLED_Print(StringToPrint, FontName, FontSize, ClearWidth, ClearHeight, Clear=1, XLoc=0, YLoc=0):
	font = ImageFont.truetype(FontName, FontSize)
	
	if (DisplayAttached):
		# Optional Clear will clear the defined area by over writing with a black rectangle. 
		if (Clear):
			draw.rectangle((0,0,ClearWidth,ClearHeight), outline=0, fill=0)
			disp.image(image)
			disp.display()

		# Write the text.  It is the caller's responsibility to ensure string fits
		draw.text((XLoc, YLoc),   StringToPrint,  font=font, fill=255)

		# Display image.
		disp.image(image)
		disp.display()


	
# 128x64 display with hardware I2C - Setting it up. 
disp = Adafruit_SSD1306.SSD1306_128_64(rst=24, i2c_address=0x3C)


# Initialize library.
try:
	disp.begin()
	# Clear display.
	disp.clear()
	disp.display()
	
	# Display is available
	DisplayAttached = 1
	# Getting ready to put images on screen
	image = Image.new('1', (disp.width, disp.height))

	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)
except:
	DisplayAttached = 0
	print ("No Display - print to terminal only.")



# Putting start up.
OLED_Print("Headless","Verdana.ttf", 12, disp.width, disp.height)
time.sleep(1)

Continue =1

while (Continue):
	# Get IP Address and format it.
	IP_Address = run_cmd("hostname -I")
	IP_String = "{}".format(IP_Address)
	IP_String = "IP{}".format(IP_String[2:-3])
	
	# Print it out to the screen.
	OLED_Print(IP_String,"Verdana.ttf", 12, disp.width, disp.height, XLoc=0, YLoc=30)

	# Get scan information
	WiFiScan = run_cmd("iw wlan0 scan")
	WiFiScanStr = "{}" .format(WiFiScan)

	# Looking through and grabbing all the SSIDs listed, including the ones that are not associated. 
	# Have to use \\\\ due to python strangeness for escapting \
	SSIDList = re.findall("SSID\: (.*?)\\\\n", WiFiScanStr)
	
	# Scan through to find the associated SSID. 
	AssociatedSSID = re.search("associated.*?SSID\: (.*?)\\\\n", WiFiScanStr)
	if (AssociatedSSID!=None):	
		AssociatedSSIDStr = ("*{}" .format(AssociatedSSID.group(1)))
	else:
		AssociatedSSIDStr = "None"

	# Display the associated SSID
	OLED_Print(AssociatedSSIDStr,"Verdana.ttf", 12, disp.width, disp.height, Clear=0, XLoc=0, YLoc=45)
	
	SSIDNum=0

	# Go through the list of SSIDs that were scanned. 
	for SSID in SSIDList:
		SSID= ("{}.{}" .format(SSIDNum, SSID))
		print(SSID)
		SSIDNum+=1
		# Clearing only 20 pixel height
		OLED_Print(SSID,"Verdana.ttf", 12, disp.width, 20)
		time.sleep(2)
	
	''' Still working on this bit to get the header information and the SSID/pwd pairs to rebuild file later. 
	
	# Open the wpa_supplicant file and get the current list of SSIDs and passwords
	wpa_supp_file = open("/etc/wpa_supplicant/wpa_supplicant.conf",  "r")
	wpa_file_contents = wpa_supp_file.read()

	# Grab the information at the start of the file.
	# Still working on this - getting existing passwords
	# FileHeader = re.search("(.*)network?", wpa_file_contents, flags = re.MULTILINE)
	# print (FileHeader)
	
	
	# Grab all the SSID Information - SSID, Password, key_mgmt 
	wpa_SSIDList = re.findall("network{.*ssid=(.*)}?", wpa_file_contents)
	
	print (wpa_SSIDList)
	'''
	
	# Menu to add new details in or rescan for SSIDs.
	MenuStr = "1.SSID 2.Scan 3.Exit"
	OLED_Print(MenuStr,"Verdana.ttf", 12, disp.width, 20)
	NextAction = input(MenuStr)
	
	# If next action is to enter new SSID, get details (SSID and password).
	# If they confirm the details, then write that to the wpa_supplicant file, which
	# has the necessary data to connect to the WiFi.
	if NextAction =='1':
		AssocStr = "Assoc SSID#?"
		OLED_Print(AssocStr,"Verdana.ttf", 12, disp.width, disp.height)
		SSID_Assoc = input(AssocStr)
		PasswordStr = "Pswd:"
		OLED_Print(PasswordStr,"Verdana.ttf", 12, disp.width, disp.height)
		Password = input(PasswordStr)

		# Confirm the user is happy with what they have entered
		ConfirmStr = 'Please confirm [Enter]:'
		print(ConfirmStr)
		OLED_Print(ConfirmStr,"Verdana.ttf", 12, disp.width, disp.height)
		time.sleep(1.5)
		SSIDStr='\tssid="{}"'.format(SSIDList[int(SSID_Assoc)])
		
		OLED_Print(SSIDStr,"Verdana.ttf", 12, disp.width, disp.height)
		input(SSIDStr)
		#time.sleep(1.5)
		passStr='\tpsk="{}"'.format(Password)
		OLED_Print(passStr,"Verdana.ttf", 12, disp.width, disp.height)
		input(passStr)
		#time.sleep(1.5)
		OLED_Print("Confirmed[y/n]","Verdana.ttf", 12, disp.width, disp.height)
		Confirmed = input("Confirmed[y/n]")
		
		# If all confirmed, then proceed with the writing to the file.  Note that 
		# this code only appends, so if a mistake is made, it cannot be corrected via
		# this programme.  
		if (Confirmed == "y" or Confirmed == "Y"):
			print("Write to WPA_Supplicant")
			print("\nnetwork={")
			print('\tssid="{}"'.format(SSIDList[int(SSID_Assoc)]))
			print('\tpsk="{}"'.format(Password))
			print('\tkey_mgmt=WPA-PSK')
			print("}\n")
			wpa_supp_file = open("/etc/wpa_supplicant/wpa_supplicant.conf",  "a+")
			wpa_supp_file.write("\nnetwork={\n")
			wpa_supp_file.write(SSIDStr + "\n")
			wpa_supp_file.write(passStr + "\n")
			wpa_supp_file.write('\tkey_mgmt=WPA-PSK\n')
			wpa_supp_file.write("}\n")
			wpa_supp_file.close()
		
	elif  NextAction =='3':
		Continue = 0

