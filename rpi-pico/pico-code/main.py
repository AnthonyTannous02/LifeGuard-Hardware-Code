from utime import sleep
from sensors import Sensors as Ss
from wifi import Wifi
import MPU6050 as MPU6050
import _thread, json

TO_SEND = {"data": {}}

# def slow_thread():
#     uart, gps = Ss.setup_gps()
#     while True:
#         gps_data = Ss.gather_data_GPS(uart, gps)
#         if gps_data != None:
#             with lock:
#                 TO_SEND["data"]["gps_data"] = gps_data


if __name__ == "__main__":
    w = Wifi()
    w.reset()
    w.connect("testssid", "testpass")
    resp = w.setup_url("http://test.com/")
    
    uart, gps = Ss.setup_gps()
    i2c = Ss.setup_i2c()
    mpu = Ss.setup_acc(i2c)
    while True:
        while "MESSAGE" not in resp:            ## TODO: Add a way to buffer the data while the PICO is waiting for "MESSAGE"
            resp = w.catch_msg()
            print(resp)
        gps_data = Ss.gather_data_GPS(uart, gps)
        acc_data = Ss.gather_data_Acc(i2c, mpu)
        print(gps_data, acc_data)
        TO_SEND["data"]["gps_data"] = gps_data
        TO_SEND["data"]["acc_data"] = acc_data
        w.send_cmd(json.dumps(TO_SEND["data"]))
        sleep(1)