# coding: utf-8

# flask
from flask import Flask, render_template

#request
from flask import request

#CORS
from flask_cors import CORS

#requests
import requests
import json
import logging
import datetime

import lcddriver
import time

###############################################################

# 센서 값 정의하기

import time
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as gpio
import logging
#############################################################
# 지문인식 센서 감지 log 남기기
date = str(datetime.date.today())

logger = logging.getLogger('fingerprintlog')
hand = logging.FileHandler(date + '.log')


#                              생성시간,   로그레벨 ,       프로세스ID,   메시지
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(process)d %(message)s')

# 파일핸들러에 문자열 포메터를 등록
hand.setFormatter(formatter)

logger.addHandler(hand)

logger.setLevel(logging.INFO)

#############################################################3

enrol = 5  # 새로운 지문을 등록하는 버튼

led = 16  # 미니 전구

HIGH = 1
LOW = 0

match = False

##############################################################

# GPIO핀 초기화 하기(초기 값으로 설정)

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

gpio.setup(enrol, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(led, gpio.OUT)

display = lcddriver.lcd()

################################################################

def lcdprint(Str):
    display.lcd_display_string(Str,1)
    
def lcdprint2(Str1,Str2):
    display.lcd_display_string(Str1,1)
    display.lcd_display_string(Str2,2)

def lcdclear():
    display.lcd_clear()

######################################################
    
######################################################

######################################################

# 새로운 지문을 등록하는 함수

def enrollFinger():
    lcdprint2("  new finger  ","  enroll system  ")
    time.sleep(2)
    print('wait please...')
    lcdprint("put new finger.")
    print("put new finger.")
    
    while ( f.readImage() == False ): # f.readImage : 센서가 지문을 읽는 것 ! # 지문이 인식되기를 기다림
        pass
    f.convertImage(0x01)
    result = f.searchTemplate()
    positionNumber = result[0] 

    if ( positionNumber >= 0 ):
        print('this finger exists aleady : #' + str(positionNumber))
        lcdprint2("  this finger  "," exists aleady ")
        time.sleep(2)
        return

    # 새로운 지문이라면, 위 if문 에 안걸린다! 바로 아래 코드 실행.


    print('remove your finger...') # 지문을 등록시에, 두번 인식을 해서 지문 등록 정확성을 up시킨다.
    lcdprint(" remove finger ")
    time.sleep(2)
    print(' wait please... ')
    lcdprint2("  put your   ","   finger again   ")
    
    while ( f.readImage() == False ): # 두번째 인식. # 지문이 인식되기를 기다림.
        pass
    f.convertImage(0x02)
    
    if ( f.compareCharacteristics() == 0 ):
        print (" this finger nomatch ")
        lcdprint2("  this finger  "," nomatch  ")
        time.sleep(2)
        return
    
    # 두번째 인식 때, 지문이 일치했다면 위 if문 에 안걸린다! 바로 아래 코드 실행.
    
    f.createTemplate() # 새로운 지문이 완벽히 등록 되었을 때
    positionNumber = f.storeTemplate()
    print('new finger enrolls sucessfully')
    lcdprint(" new finger enroll : " + str(positionNumber))
    print(' new finger enroll : #' + str(positionNumber))
    logger.error('newfinger')
    time.sleep(2)

############################################################## 

# 일치하는 지문을 찾는 함수
def searchFinger():
    try:
        print('wait please...')
        while( f.readImage() == False ):
            #pass
            time.sleep(.5)
            return
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        accuracyScore = result[1]
        
        if positionNumber == -1 :
            print(' Fail! match finger is not here')
            lcdprint(" Fail! ")
            logger.warning('nomatch')   
            time.sleep(2)
            return
        
        else:
            print(' Success! Sensor finds match finger : #' + str(positionNumber))
            lcdprint(" Success! : " + str(positionNumber)) 
            logger.info('match')
            match = True
            time.sleep(2)
            
             # 지문이 일치하면, 문이 열리도록 아래에 코드 추가할 예정.
    except Exception as e:
        print('sensor function is interrupted')
        print('exception message: ' + str(e))
        exit(1)
    
#####################################################
####### START ############

# 지문인식센서 초기화 하기(초기 값으로 설정)

try:
    print('sensor initianlize~!!!')
    lcdprint("*** SYSTEM ***")
    time.sleep(2)
    lcdprint2(" Finger sensor"," Initialize")
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    
    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')
    
except Exception as e:
    print('Exception message: ' + str(e))
    exit(1)


# 지문인식센서를 시작할 때

lcdprint(" finger print system ")
time.sleep(3)
lcdprint(" system starts ")
time.sleep(3)
flag=0
lcdclear()
while 1:
    gpio.output(led, HIGH) # 지문등록시에만 미니전구 꺼지고, 다른 때엔 항상 켜지게 할 것
    lcdprint2("  put your  ","finger") # 계속 반복
   
    if gpio.input(enrol) == 0: #새로운 지문을 등록하려면 enrol 버튼을 눌러야 한다.
        gpio.output(led, HIGH)
        time.sleep(1)
        gpio.output(led, LOW)
        time.sleep(1)
        enrollFinger()

    else:
        searchFinger() # 새로운 지문 등록시 외에..계속 실행되는 함수
