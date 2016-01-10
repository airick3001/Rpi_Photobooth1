#IMPORTS
import RPi.GPIO as gpio
import picamera
import pygame
import time
import os
import PIL.Image
import ImageDraw
import cups

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image


#initialise global variables
closeme = True #Loop Control Variable
timepulse = 999 #Pulse Rate of LED
LEDon = False #LED Flashing Control
gpio.setmode(gpio.BCM) #Set GPIO to BCM Layout
Numeral = "" #Numeral is the number display
Message = "" #Message is a fullscreen message
SmallMessage = "" #SmallMessage is a lower banner message
TotalImageCount = 1 #Counter for Display and to monitor paper usage
PhotosPerCart = 16 #Selphy takes 16 sheets per tray

#initialise pygame
pygame.mixer.pre_init(44100, -16, 1, 1024*3) #PreInit Music, plays faster
pygame.init() #Initialise pygame
screen = pygame.display.set_mode((800,480),pygame.FULLSCREEN) #Full screen 640x480
background = pygame.Surface(screen.get_size()) #Create the background object
background = background.convert() #Convert it to a background

#UpdateDisplay - Thread to update the display, neat generic procedure
def UpdateDisplay():
   #init global variables from main thread
   global Numeral
   global Message
   global SmallMessage
   global TotalImageCount
   global screen
   global background
   global pygame

   SmallText = "Matt Cam" #Default Small Message Text   
   if(TotalImageCount >= (PhotosPerCart - 2)): #Low Paper Warning at 2 images less
      SmallText = "Paper Running Low!..."
   if(TotalImageCount >= PhotosPerCart): #Paper out warning when over Photos per cart
      SmallMessage = "Paper Out!..."
      TotalImageCount = 0 
   background.fill(pygame.Color("black")) #Black background
   smallfont = pygame.font.Font(None, 50) #Small font for banner message
   SmallText = smallfont.render(SmallText,1, (255,0,0))
   background.blit(SmallText,(10,445)) #Write the small text
   SmallText = smallfont.render(`TotalImageCount`+"/"+`PhotosPerCart`,1, (255,0,0))
   background.blit(SmallText,(710,445)) #Write the image counter

   if(Message != ""): #If the big message exits write it
      font = pygame.font.Font(None, 180)
      text = font.render(Message, 1, (255,0,0))
      textpos = text.get_rect()
      textpos.centerx = background.get_rect().centerx
      textpos.centery = background.get_rect().centery
      background.blit(text, textpos)
   elif(Numeral != ""): # Else if the number exists display it
      font = pygame.font.Font(None, 800)
      text = font.render(Numeral, 1, (255,0,0))
      textpos = text.get_rect()
      textpos.centerx = background.get_rect().centerx
      textpos.centery = background.get_rect().centery
      background.blit(text, textpos)

   screen.blit(background, (0,0))
   pygame.draw.rect(screen,pygame.Color("red"),(10,10,770,430),2) #Draw the red outer box
   pygame.display.flip()
   
   return
#Pulse Thread - Used to pulse the LED without slowing down the rest
def pulse(threadName, *args):
        #gpio.setmode(gpio.BCM)
   global gpio
        gpio.setup(17, gpio.OUT)
   
   #print timepulse
          while closeme:
             global LEDon

                #print LEDon
                
                if timepulse == 999:
                        gpio.output(17, False)
                        LEDon = True
                else:
                        if LEDon:
                                gpio.output(17, True)
                                time.sleep(timepulse)
                                LEDon = False
                        else:
                                gpio.output(17, False)
                                time.sleep(timepulse)
                                LEDon = True

#Main Thread
def main(threadName, *args):

   #Setup Variables
        gpio.setup(24, gpio.IN) #Button on Pin 24 Reprints last image
        gpio.setup(22, gpio.IN) #Button on Pin 22 is the shutter
        global closeme
        global timepulse
   global TotalImageCount
   global Numeral
   global SmallMessage
   global Message
      
   Message = "Loading..."
        UpdateDisplay()
   time.sleep(5) #5 Second delay to allow USB to mount

        #Initialise the camera object
        camera = picamera.PiCamera()
        #Transparency allows pigame to shine through
        camera.preview_alpha = 120
        camera.vflip = False
        camera.hflip = True
        camera.rotation = 90
        camera.brightness = 45
        camera.exposure_compensation = 6
        camera.contrast = 8
        camera.resolution = (1280,720)
        #Start the preview
        camera.start_preview()
