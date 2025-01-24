import time
import struct
from machine import Pin, I2C
import i2cEncoderLibV2

I2C_BUS = 1
I2C_SCL_PIN = 33
I2C_SDA_PIN = 32
INTERRUPT_PIN = 34
ENCODER_ADDRESSES = [0x50, 0x30, 0x60, 0x44]

# Initialize the interrupt pin.
INT_pin = Pin(INTERRUPT_PIN, Pin.IN, Pin.PULL_UP)

# Initialize the I2C bus.
i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))

# Create the encoders array using a loop.
encoders = [i2cEncoderLibV2.i2cEncoderLibV2(i2c, addr) for addr in ENCODER_ADDRESSES]

# Unified callback functions.
def EncoderChange(encoder):
    encoder.writeLEDR(100)
    valBytes = struct.unpack('>i', encoder.readCounter32())
    print(f'Changed: {valBytes[0]} on Encoder with address: {hex(encoder.readI2CAdd())}')
    encoder.writeLEDR(0)

def EncoderPush(encoder):
    encoder.writeLEDR(100)
    print(f'Encoder Pushed on Encoder with address: {hex(encoder.readI2CAdd())}')
    encoder.writeLEDR(0)

# Interrupt handler.
def Encoder_INT(pin):
    if pin.value() == 0:
        # Disable the interrupt.
        INT_pin.irq(handler=None)
        # Loop over all encoders to find the triggering instance.
        for encoder in encoders:
            # Read and reset the status.
            status = encoder.readEncoder8(i2cEncoderLibV2.REG_ESTATUS)
            # Fire the appropriate callback.
            if status & (i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC):
                EncoderChange(encoder)
            if status & i2cEncoderLibV2.PUSHP:
                EncoderPush(encoder)
        # Re-enable the interrupt.
        INT_pin.irq(trigger=Pin.IRQ_FALLING, handler=Encoder_INT)

# Initialize a specific encoder.
def init_encoder(encoder):
    encoder.reset()
    print("Encoder reset")
    time.sleep(0.1)

    encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
                 | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
                 | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
    encoder.begin(encconfig)
    print(f"Encoder begin with config: {encconfig}")

    reg = (i2cEncoderLibV2.PUSHP | i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC)
    encoder.writeEncoder8(i2cEncoderLibV2.REG_INTCONF, reg)
    print(f"Encoder begin with intconfig: {reg}")

    encoder.writeCounter(0)
    encoder.writeMax(35)
    encoder.writeMin(-20)
    encoder.writeStep(1)
    encoder.writeAntibouncingPeriod(12)

    print(f'Board ID code: 0x{encoder.readIDCode():X}')
    print(f'Board Version: 0x{encoder.readVersion():X}')

# Initialize each encoder.
for encoder in encoders:
    init_encoder(encoder)

# Setup the interrupt handler.
INT_pin.irq(trigger=Pin.IRQ_FALLING, handler=Encoder_INT)

