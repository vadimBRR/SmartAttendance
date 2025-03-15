from machine import Pin, PWM
import time

class BuzzerController:
    def __init__(self, pin):

        self.buzzer = PWM(Pin(pin))
        self.stop()  

    def play_tone(self, frequency, duration):
       
        self.buzzer.freq(frequency)  
        self.buzzer.duty_u16(32768) 
        time.sleep(duration)  
        self.buzzer.duty_u16(0)  

    def stop(self):

        print("stop buzzer")
        self.buzzer.duty_u16(0) 
