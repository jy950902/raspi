from spidev import SpiDev
import RPi.GPIO as GPIO
import time
import logging

#############################################################################
# ADC 컨버터 함수 설정
class MCP3008:
    def __init__(self, bus = 0, device = 0):
        self.bus, self.device = bus, device
        self.spi = SpiDev()
        self.open()

    def open(self):
        self.spi.open(self.bus, self.device)

    def read(self, channel = 0):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def close(self):
        self.spi.close()

#############################################################################
# log
logger = logging.getLogger('myApp')
hand = logging.FileHandler('myapp_.log')

#                              생성시간,   로그레벨 ,       프로세스ID,   메시지
formatter = logging.Formatter('%(asctime)s %(levelname)s %(process)d %(message)s')

# 파일핸들러에 문자열 포메터를 등록
hand.setFormatter(formatter)

logger.addHandler(hand)

logger.setLevel(logging.INFO)
#############################################################################

LED=16   
pir_s=25
GPIO_TRIGGER = 18
GPIO_ECHO = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(pir_s, GPIO.IN)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT) 
GPIO.setup(GPIO_ECHO,GPIO.IN)

adc = MCP3008()

try:
    while True:
        adc_value = adc.read( channel = 0 ) # 조도센서 값 읽어오기

        stop = 0
        start = 0
        # 먼저 트리거 핀을 OFF 상태로 유지한다
        GPIO.output(GPIO_TRIGGER, False)
        time.sleep(2)
 
        # 10us 펄스를 내보낸다. 
        # 파이썬에서 이 펄스는 실제 100us 근처가 될 것이다.
        # 하지만 HC-SR04 센서는 이 오차를 받아준다.
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.1)
        GPIO.output(GPIO_TRIGGER, False)
 
        # 에코 핀이 ON되는 시점을 시작 시간으로 잡는다.
        while GPIO.input(GPIO_ECHO)==0:
            start = time.time()
 
        # 에코 핀이 다시 OFF되는 시점을 반사파 수신 시간으로 잡는다.
        while GPIO.input(GPIO_ECHO)==1:
            stop = time.time()

        # Calculate pulse length
        elapsed = stop-start

        # 초음파는 반사파이기 때문에 실제 이동 거리는 2배이다. 따라서 2로 나눈다.
        # 음속은 편의상 340m/s로 계산한다. 현재 온도를 반영해서 보정할 수 있다.
        if (stop and start):
            distance = (elapsed * 34000.0) / 2
            print("Distance : %.1f cm" % distance)
            if distance <= 150:
                logger.warning('사람 있음')
                if (adc_value == 0): # 조도센서 값이 0이면 (=>어두우면)
                    print("LED ON : PIR %d"%adc_value)
                    GPIO.output(LED, True) # 불이 켜짐
                    logger.info('불켜짐')
                    time.sleep(2)
                else:
                    print("LED OFF : PIR %d"%adc_value) # 조도센서 값이 0이 아니면 (=>빛이 조금이라도 있으면)
                    GPIO.output(LED, False) # 불이 꺼짐
                    logger.debug('틀렸음~!!')
                    time.sleep(2)
            else:
                GPIO.output(LED, False)
                logger.error('사람 없음!')
                

except KeyboardInterrupt:
    adc.close()
    GPIO.cleanup()
    