import pigpio
import time
import subprocess


SPEED_PULS_INPUT = 6
TIRE_circumference = 1.841 #単位はメートル

pi = pigpio.pi()
pi.set_mode(SPEED_PULS_INPUT, pigpio.INPUT)

t_now = 0
t_last = 0


def cbf(gpio, level, tick):  # call back function for pulse detect _/~~\__
    global t_now, t_last

    if (level == 1):  # right after the rising edge
        
        t_now = tick
        if (t_now >= t_last):  # if wrapped 32bit value,
            timepassed = t_now - t_last
        else:
            timepassed = t_now + (0xffffffff + 1 - t_last)

        # microseconds to seconds, per_second to per_hour
        speed =  (TIRE_circumference / (timepassed / 1000000)) * 3.6
        t_last = t_now
        Display_Comand = ["figlet", str(int(speed))]
        subprocess.call(Display_Comand)


cb = pi.callback(SPEED_PULS_INPUT, pigpio.RISING_EDGE, cbf)
pause()
pi.stop()