#!/bin/python3

from sys import argv
from time import sleep
from logging import basicConfig, info, debug, error, INFO
from subprocess import run, check_output
from signal import signal, SIGTERM
from datetime import datetime

from libs.oled import Oled
from libs.stats import hardware_stats, disk_stats, ips, temp
import RPi.GPIO as GPIO

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATEFORMAT = datetime.now().strftime("%Y%m%d%H%M")
basicConfig(
    filename='/var/log/naspi%s.log' % DATEFORMAT,
    filemode='w',
    format=LOG_FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=INFO
)

GPIO_SWITCH = 23
GPIO_OLED = 4
GPIO_FAN = 18

WAIT_TIME = 5
PRESS_TIME = 1
LONG_PRESS = 10 / WAIT_TIME  # 10s long press for quick shutdown

OLED_LINES = [
    -4,
    5,
    14,
    23
]

fan_pwm = None
PWM_FREQ = 1000
FAN_OFF = 0
FAN_LOW = 25
FAN_HIGH = 100

OFF_TEMP = 23
MIN_TEMP = 30
MAX_TEMP = 50

FAN_GAIN = float(FAN_HIGH - FAN_LOW) / float(MAX_TEMP - MIN_TEMP)


def gpio_setup():
    global fan_pwm, PWM_FREQ
    global GPIO_OLED, GPIO_FAN

    # Disable warnings
    GPIO.setwarnings(False)

    # turn on gpio pins
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(GPIO_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Turn on Oled Display
    GPIO.setup(GPIO_OLED, GPIO.OUT)
    GPIO.output(GPIO_OLED, GPIO.HIGH)

    # Turn on Fan PWM
    # GPIO.setup(GPIO_FAN, GPIO.OUT)
    # fan_pwm = GPIO.PWM(GPIO_FAN, PWM_FREQ)
    # fan_pwm.start(0)

    GPIO.setup(GPIO_FAN, GPIO.OUT, initial=GPIO.LOW)
    fan_pwm = GPIO.PWM(GPIO_FAN, PWM_FREQ)


def on_off(data):
    info(data)
    info('Shutdown!')


def is_boot_complete():
    # Run Levels
    # 0	poweroff.target	Apagado del sistema
    # 1	rescue.target	Shell de rescate
    # 2	multi-user.target	Sistema no gráfico
    # 3	multi-user.target	Sistema no gráfico
    # 4	multi-user.target	Sistema no gráfico
    # 5	multi-user.target	Sistema gráfico
    # 6	reboot.target	Apagado y reinicio
    try:
        cmd = 'who -r'
        result = check_output(cmd, shell=True)
        _, runlevel, _, _, _ = result.decode('utf-8').strip().split(' ')

        return True if int(runlevel) >= 3 and int(runlevel) <= 5 else False

    except:
        return False

def normal_shutdown():
    info('Normal Shutdown')
    run(['sudo', 'poweroff'])


def quick_shutdown():
    info('Quick Shutdown')


def init_shutdown(press_time):
    global LONG_PRESS
    if press_time >= LONG_PRESS:
        quick_shutdown()
    else:
        normal_shutdown()

def shutdown():
    screen = Oled()
    info('Ending script')

    GPIO.cleanup()

    screen.write('Shutdown!', 0, 10)
    screen.show()

    control_fan(100)
    exit(0)


def handle_sigterm(self, sig):
    shutdown()


def control_fan(temp):
    global fan_pwm
    global OFF_TEMP, MIN_TEMP, MAX_TEMP
    global FAN_OFF, FAN_LOW, FAN_HIGH, FAN_GAIN

    if type(temp) is str:
        temp = float(temp.replace('\'C', '').strip())

    if temp <= OFF_TEMP:
        dutyCycle = FAN_OFF

    elif temp > OFF_TEMP and temp < MAX_TEMP:
        # delta = min(temp, MAX_TEMP) - MIN_TEMP
        # velocity = FAN_LOW + delta * FAN_GAIN)
        dutyCycle = int(FAN_LOW + (min(temp, MAX_TEMP) - MIN_TEMP) * FAN_GAIN)

    else:
        dutyCycle = FAN_HIGH

    info('Temperature: %s\'C - Duty Cycle: %s' % (temp, dutyCycle))
    fan_pwm.start(dutyCycle)


if __name__ == '__main__':
    info('Init Script!!!')

    signal(SIGTERM, handle_sigterm)

    gpio_setup()
    screen = Oled()

    disks = [
        '/',
        '/NAS'
    ]

    try:
        while True:
            lines = []
            screen.clear()

            # screen.write('Mode %s' % mode, 0, 10)
            # if GPIO.input(GPIO_SWITCH) == 0:
            #     info('Button press!!!')
            #     PRESS_TIME += 1
            #     init_shutdown(PRESS_TIME)
            # else:
            #     PRESS_TIME = 0

            if is_boot_complete(): #standby
                s = hardware_stats()
                d = disk_stats(disks)
                ip = ips()
                t = temp()

                line = 0
                x = 0
                for part, stat in s:
                    if len(stat) != 8:
                        stat = stat.rjust(8, ' ')
                    screen.write('%s:%s' % (part, stat), (x * 66) - 1, OLED_LINES[line])
                    x += 1

                line += 1
                for disk, size, stat  in d:
                    if len(size) != 11:
                        size = size.rjust(11, ' ')

                    if len(stat) != 7:
                        stat = stat.rjust(7, ' ')

                    screen.write('%s' % disk, 0, OLED_LINES[line])
                    screen.write('%s' % size, 28, OLED_LINES[line])
                    screen.write('%s' % stat, 90, OLED_LINES[line])

                    line += 1

                screen.write('IP: %s' % ip, 0, OLED_LINES[line])
                screen.write('T: %s' % t, 88, OLED_LINES[line])
                control_fan(t)

            else:
                try:
                    if point is None:
                        point = 0

                except:
                    point = 0

                text = 'Booting{}'.format(''.join(['.' for _ in range(point)]))
                screen.write(text, 0, 10)

                point = point + 1 if point < 4 else 0
                control_fan(100)

            screen.show()
            sleep(WAIT_TIME)

    except KeyboardInterrupt:
        info('Stoping...')

    except Exception as e:
        from traceback import print_exc
        print_exc()
        error("Exception occurred", exc_info=True)
        screen.clear()
        screen.write('ERROR!!!', 0, 10)
        screen.show()

    finally:
        shutdown()

