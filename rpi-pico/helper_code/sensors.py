from machine import Pin, UART, I2C
from micropyGPS import MicropyGPS
from MPU6050 import MPU6050
from max30102.max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM

class Sensors():
    @staticmethod   
    def setup_i2c():
        i2c = I2C(0, sda=Pin(16), scl=Pin(17))
        return i2c
    
    @staticmethod   
    def setup_gps():
        uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=300)
        gps = MicropyGPS(2)
        return uart, gps    
    
    @staticmethod   
    def setup_acc(i2c: I2C):
        mpu = MPU6050(i2c)
        mpu.wake()
        return mpu
    
    @staticmethod
    def setup_oxi(i2c: I2C):
        max3 = MAX30102(i2c)
        if max3.i2c_address not in i2c.scan():
            print("Sensor not found.")
            return
        elif not (max3.check_part_id()):
            # Check that the targeted sensor is compatible
            print("I2C device ID not corresponding to MAX30102 or MAX30105.")
            return
        else:
            print("Sensor connected and recognized.")
        
        max3.setup_sensor()
        sensor_sample_rate = 400
        max3.set_sample_rate(sensor_sample_rate)
        sensor_fifo_average = 4
        max3.set_fifo_average(sensor_fifo_average)
        max3.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM) # LED brightness
        return max3
    
    @staticmethod
    def gather_data_GPS(uart : UART, gps : MicropyGPS):
        data = bytearray(b'')
        while uart.any(): 
            data = (uart.read())
            for x in data:
                gps.update(chr(x))
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
    def gather_data_Oxi(i2c : I2C, max3 : MAX30102): ## TODO: Implement the actual sensor
        max3.check() # Check if the storage contains available samples
        if max3.available():
            # Access the storage FIFO and gather the readings (integers)
            red_reading = max3.pop_red_from_storage()
            ir_reading = max3.pop_ir_from_storage()
            return {
                'IR': ir_reading,
                'RED': red_reading
            }
        return {
            'IR': -1,
            'RED': -1
        }
    