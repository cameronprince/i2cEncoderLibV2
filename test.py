import time
import struct
from machine import Pin, I2C
import i2cEncoderLibV2

I2C_BUS = 1
I2C_SCL_PIN = 19
I2C_SDA_PIN = 18
INTERRUPT_PIN = 22
BOARD_ID = 0x50

# Setup the Interrupt Pin from the encoder.
INT_pin = Pin(INTERRUPT_PIN, Pin.IN, Pin.PULL_UP)

# Initialize the device.
i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))

encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, BOARD_ID)

def EncoderChange():
    encoder.writeLEDG(100)
    valBytes = struct.unpack('>i', encoder.readCounter32())
    print('Changed: %d' % valBytes[0])
    encoder.writeLEDG(0)

def EncoderPush():
    encoder.writeLEDB(100)
    print('Encoder Pushed!')
    encoder.writeLEDB(0)

def EncoderDoublePush():
    encoder.writeLEDB(100)
    encoder.writeLEDG(100)
    print('Encoder Double Push!')
    encoder.writeLEDB(0)
    encoder.writeLEDG(0)

def EncoderMax():
    encoder.writeLEDR(100)
    print('Encoder max!')
    encoder.writeLEDR(0)

def EncoderMin():
    encoder.writeLEDR(100)
    print('Encoder min!')
    encoder.writeLEDR(0)

def Encoder_INT(pin):
    encoder.updateStatus()

# Initialize encoder
encoder.reset()
print("Encoder reset")
time.sleep(0.1)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
             | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
             | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
encoder.begin(encconfig)
print("Encoder begin with config:", encconfig)

encoder.writeCounter(0)
encoder.writeMax(35)
encoder.writeMin(-20)
encoder.writeStep(1)
encoder.writeAntibouncingPeriod(8)
encoder.writeDoublePushPeriod(50)
encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)

encoder.onChange = EncoderChange
encoder.onButtonPush = EncoderPush
encoder.onButtonDoublePush = EncoderDoublePush
encoder.onMax = EncoderMax
encoder.onMin = EncoderMin

encoder.autoconfigInterrupt()
print('Board ID code: 0x%X' % encoder.readIDCode())
print('Board Version: 0x%X' % encoder.readVersion())

encoder.writeRGBCode(0x640000)
time.sleep(0.3)
encoder.writeRGBCode(0x006400)
time.sleep(0.3)
encoder.writeRGBCode(0x000064)
time.sleep(0.3)
encoder.writeRGBCode(0x00)

# Setup an interrupt handler
INT_pin.irq(trigger=Pin.IRQ_FALLING, handler=Encoder_INT)

while True:
    # For debugging, we can poll status
    encoder.updateStatus()
    time.sleep(0.1)
