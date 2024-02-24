from utime import sleep
from helper_code.sensors import Sensors as Ss
from helper_code.wifi import Wifi
import MPU6050 as MPU6050
from max30102.max30102 import MAX30102
import time
import _thread
import json
ACC_DATA = {"Gyro": [], "Accel": []}
OXI_DATA = {"RED": [], "IR": []}
GPS_DATA = {}

def fast_thread(data_lock, i2c, mpu, max3):
    while True:
        acc_data = Ss.gather_data_Acc(i2c, mpu)
        oxi_data = Ss.gather_data_Oxi(i2c, max3)
        with data_lock:
            ACC_DATA["Gyro"].append(acc_data["Gyro"])
            ACC_DATA["Accel"].append(acc_data["Accel"])
            OXI_DATA["RED"].append(oxi_data["RED"])
            OXI_DATA["IR"].append(oxi_data["IR"])
        sleep(0.05)
        

if __name__ == "__main__":
    w = Wifi()
    resp = w.setup("OGERO DSL", "16005242", "http://192.168.1.103:5000")
    
    data_lock = _thread.allocate_lock()
    uart, gps = Ss.setup_gps()
    i2c = Ss.setup_i2c()
    mpu = Ss.setup_acc(i2c)
    max3 = Ss.setup_oxi(i2c)
    _thread.start_new_thread(fast_thread, (data_lock, i2c, mpu, max3)) 
    while True:
        with data_lock:
            gps_data = Ss.gather_data_GPS(uart, gps)
            GPS_DATA.update(gps_data)
        sleep(0.2)
        with data_lock:
            resp = w.send_type(resp, "ACC")
            resp = w.send_data(resp, json.dumps(ACC_DATA))
            ACC_DATA = {"Gyro": [], "Accel": []}
        sleep(0.2)
        with data_lock:
            resp = w.send_type(resp, "OXI")
            resp = w.send_data(resp, json.dumps(OXI_DATA))
            OXI_DATA = {"RED": [], "IR": []}
        sleep(0.2)
        with data_lock:
            resp = w.send_type(resp, "GPS")
            resp = w.send_data(resp, json.dumps(GPS_DATA))
            GPS_DATA.clear()
