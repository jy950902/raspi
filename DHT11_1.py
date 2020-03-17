import Adafruit_DHT
import time
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
A = 17 #모터 A핀
B = 27 #모터 B핀

#A,B GPIO setup설정
GPIO.setup(A,GPIO.OUT,initial=GPIO.LOW) 
GPIO.setup(B,GPIO.OUT,initial=GPIO.LOW)

#온습도센서
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 19

#회전의 강도
def high_wind():
    print("선풍기를 강풍으로 가동합니다.")
    p1=GPIO.PWM(A,30)
    p2=GPIO.PWM(B,30)
    p1.start(30)
    time.sleep(5)
    p1.stop()
    p2.start(30)
    time.sleep(5)
    p2.stop()

def low_wind():
    print("선풍기를 약풍으로 가동합니다.")
    p1=GPIO.PWM(A,20)
    p2=GPIO.PWM(B,20)
    p1.start(20)
    time.sleep(5)
    p1.stop()
    p2.start(20)
    time.sleep(5)
    p2.stop()


while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))

        if(temperature >= 25.0):
            high_wind()
            print("온도를 재측정합니다.")


        elif(temperature >= 23.0):
            low_wind()
            print("온도를 재측정합니다.")
                    
        else:
            print("선풍기를 멈춥니다.")
            GPIO.output(A,GPIO.LOW)
            GPIO.output(B,GPIO.LOW)
            time.sleep(5) #5초 유지
            print("온도를 재측정합니다.")

    else:
        print("Sensor failure. Check again. ");
    time.sleep(1);

GPIO.output(A,GPIO.LOW) #정지
GPIO.output(B,GPIO.LOW)  
GPIO.cleanup()