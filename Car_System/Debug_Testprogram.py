# one shot measurement only
#
import pigpio
import time

HC_SR04_trig = 5
HC_SR04_echo = 6
TIRE_circumference = 1.818 #単位はメートル

pi = pigpio.pi()
pi.set_mode(HC_SR04_trig, pigpio.OUTPUT)
pi.set_mode(HC_SR04_echo, pigpio.INPUT)

t_now = 0
t_last = 0


def cbf(gpio, level, tick):  # call back function for pulse detect _/~~\__
    global t_now, t_last

    if (level == 1):  # right after the rising edge
        t_last = t_now
        t_now = tick
        if (t_last >= t_now):  # if wrapped 32bit value,
            timepassed = t_now - t_last
        else:
            timepassed = t_now + (0xffffffff + 1 - t_last)

        # microseconds to seconds, per_second to per_hour
        speed =  (TIRE_circumference / (timepassed / 1000000)) * 3.6
        print('{"tick":%10d, "time_us": %6d, "speed": %.2f}' % (tick, timepassed, speed))


cb = pi.callback(HC_SR04_echo, pigpio.RISING_EDGE, cbf)
pause()
pi.stop()