from machine import Pin, UART, I2C
from micropyGPS import MicropyGPS
from MPU6050 import MPU6050

class Sensors():
    @staticmethod   
    def setup_gps():
        uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=300)
        gps = MicropyGPS(2)
        return uart, gps    
    
    @staticmethod   
    def setup_i2c():
        i2c = I2C(0, sda=Pin(16), scl=Pin(17))
        return i2c
    
    @staticmethod   
    def setup_acc(i2c: I2C):
        mpu = MPU6050(i2c)
        mpu.wake()
        return mpu
    
    @staticmethod
    def gather_data_GPS(uart : UART, gps : MicropyGPS):
        data = bytearray(b'')
        while uart.any(): 
            data = (uart.read())
            for x in data:
                gps.update(chr(x))
        if(len(data) < 1):
            return None
        return {
            'latitude': gps.latitude,
            'longitude': gps.longitude,
            'altitude': gps.altitude,
            'speed': gps.speed,
            'timestamp': gps.timestamp
                }
    
    @staticmethod
    def gather_data_Acc(i2c : I2C, mpu : MPU6050):
        gyro = mpu.read_gyro_data()
        accel = mpu.read_accel_data()
        return {
            "Gyro": gyro,
            "Accel": accel
        }
    
    @staticmethod
    def gather_data_Oxi(): ## TODO: Implement the actual sensor
        return {
            'SpO2': '99',
            'BPM': '100'
        }
    