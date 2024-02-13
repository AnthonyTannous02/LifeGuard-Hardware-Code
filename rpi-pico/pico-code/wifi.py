import machine
import time
import select

RESET_PIN = machine.Pin(2, machine.Pin.OUT)

class Wifi():
    def __init__(self):
        self.uart = machine.UART(0, baudrate=115200)
    
    def connect(self, ssid, password):
        while True:
            resp = self.catch_msg()
            print(resp)
            if resp is not None:
                if "APNAME" in resp:
                    self.send_cmd(ssid)
                elif "APAUTH" in resp:
                    self.send_cmd(password)
                    break
    
    def setup_url(self, url):
        while True:
            resp = self.catch_msg()
            if resp and "API" in resp:
                self.send_cmd(url)
                break
        return self.catch_msg()
    
    def reset(self):
        RESET_PIN.value(0)
        time.sleep(0.2)
        RESET_PIN.value(1)
    
    def catch_msg(self):
        poll = select.poll()
        poll.register(self.uart, select.POLLIN)
        while True:
            if poll.poll(1000):
                try:
                    return self.uart.read().decode('utf-8').rstrip('\r\n')
                except UnicodeError:
                    return None
        
    def send_cmd(self, cmd):
        cmd += '\n';
        self.uart.write(cmd)