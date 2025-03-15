from machine import Pin, PWM

class RGBController:
    def __init__(self, red_pin, green_pin, blue_pin):
        self.red = PWM(Pin(red_pin))   
        self.green = PWM(Pin(green_pin))  
        self.blue = PWM(Pin(blue_pin))  


        for channel in [self.red, self.green, self.blue]:
            channel.freq(1000)

    def set_color(self, red=0, green=0, blue=0):

        self.red.duty_u16(int(red * 65535 / 1023))
        self.green.duty_u16(int(green * 65535 / 1023))
        self.blue.duty_u16(int(blue * 65535 / 1023))

    def off(self):

        self.set_color(0, 0, 0)
