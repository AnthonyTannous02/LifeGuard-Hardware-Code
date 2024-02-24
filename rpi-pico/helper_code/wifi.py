import machine
import time
import select

RESET_PIN = machine.Pin(2, machine.Pin.OUT)


class Wifi:
    def __init__(self):
        self.uart = machine.UART(0, baudrate=115200)
        self.uart.init(115200, bits=8, parity=None, stop=1)
    
    def setup(self, ssid, password, url):
        ## Reset the module
        RESET_PIN.value(0)
        time.sleep(0.4)
        RESET_PIN.value(1)
        
        ## Connect to the internet
        resp = ""
        while True:
            resp = self.catch_msg()
            if resp and "APNAME" in resp:
                break
        resp = self.send_cmd(ssid)
        
        while True:
            if resp and "APAUTH" in resp:
                break
            resp = self.catch_msg()
        resp = self.send_cmd(password)
        
        while True:
            if resp and "API" in resp:
                break
            resp = self.catch_msg()
        resp = self.send_cmd(url)
        
        return resp

    def send_type(self, resp, type):
        cmd = 0
        if type == "ACC":
            cmd = 1
        elif type == "GPS":
            cmd = 2
        elif type == "OXI":
            cmd = 3
        elif type == "PRS":
            cmd = 4
        
        while True:
            if resp and "TYPE" in resp:
                break
            resp = self.catch_msg()
        resp = self.send_cmd(cmd)
        return resp

    def send_data(self, resp, data):
        while True:
            if resp and "MESSAGE" in resp:
                break
            resp = self.catch_msg()
        resp = self.send_cmd(data)
        return resp

    def send_cmd(self, cmd):
        cmd = str(cmd) + "\n"
        self.uart.write(cmd)
        return self.catch_msg()

    def catch_msg(self):
        while True:
            while self.uart.any():
                resp = ""
                try:
                    resp = self.uart.read().decode("utf-8").rstrip("\r\n")
                except UnicodeError:
                    resp = None
                print(resp)
                return resp
