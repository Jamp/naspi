#!/bin/python3

from time import sleep
from subprocess import run, check_output
from signal import signal, SIGTERM

from libs.log import logger as logging
from libs.oled import Oled
from libs.stats import hardware_stats, disk_stats, get_ip, get_temperature
from libs.fan import Fan
import RPi.GPIO as GPIO

GPIO_SWITCH = 23
GPIO_OLED = 4
GPIO_FAN = 18

WAIT_TIME = 5
PRESS_TIME = 1
LONG_PRESS = 10 / WAIT_TIME  # 10s long press for quick shutdown

MOUNT_POINTS = [
    '/',
    '/NAS'
]

OLED_LINES = [
    -4,
    5,
    14,
    23
]

def gpio_setup():
    global GPIO_OLED, GPIO_FAN

    # Disable warnings
    GPIO.setwarnings(False)

    # turn on gpio pins
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(GPIO_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)


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
    logging.info('Normal Shutdown')
    run(['sudo', 'poweroff'])


def quick_shutdown():
    logging.info('Quick Shutdown')


def init_shutdown(press_time):
    global LONG_PRESS
    if press_time >= LONG_PRESS:
        quick_shutdown()
    else:
        normal_shutdown()

def shutdown():
    GPIO.cleanup()

    logging.info('Ending script')

    if not Oled.check_available():
        logging.error('Pantalla no disponible, antes de apagar')

    else:
        screen = Oled()
        screen.write('Shutdown!', 0, 10)
        screen.show()

    exit(0)


def handle_sigterm(self, sig):
    shutdown()

if __name__ == '__main__':

    logging.info('Init Script!!!')

    signal(SIGTERM, handle_sigterm)

    gpio_setup()

    # Start Display
    screen = None

    # Start Fan
    fan = Fan(GPIO_FAN)

    try:
        while True:
            if not Oled.check_available():
                logging.error('Pantalla no disponible')

                sleep(WAIT_TIME)
                continue

            if screen is None:
                screen = Oled()

            lines = []
            screen.clear()

            # screen.write('Mode %s' % mode, 0, 10)
            # if GPIO.input(GPIO_SWITCH) == 0:
            #     logging.info('Button press!!!')
            #     PRESS_TIME += 1
            #     init_shutdown(PRESS_TIME)
            # else:
            #     PRESS_TIME = 0

            if is_boot_complete(): #standby
                stats = hardware_stats()
                disks = disk_stats(MOUNT_POINTS)
                ip = get_ip()
                temperature = get_temperature()

                line = 0
                x = 0
                for part, stat in stats:
                    stat = '{:0.2f}%'.format(stat)

                    if len(stat) != 8:
                        stat = stat.rjust(8, ' ')

                    screen.write('{}:{}'.format(part, stat), (x * 66) - 1, OLED_LINES[line])
                    x += 1

                line += 1
                for disk, size, stat  in disks:
                    if len(size) != 11:
                        size = size.rjust(11, ' ')

                    if len(stat) != 7:
                        stat = stat.rjust(7, ' ')

                    screen.write(disk, 0, OLED_LINES[line])
                    screen.write(size, 28, OLED_LINES[line])
                    screen.write(stat, 90, OLED_LINES[line])

                    line += 1

                screen.write('IP: %s' % ip, 0, OLED_LINES[line])
                screen.write('T: {:0.2f}\'C'.format(temperature), 88, OLED_LINES[line])

            else:
                try:
                    if point is None:
                        point = 0

                except:
                    point = 0

                temperature = 100
                text = 'Booting{}'.format(''.join(['.' for _ in range(point)]))
                screen.write(text, 0, 10)

                point = point + 1 if point < 4 else 0

            fan.adjust(temperature)
            screen.show()
            sleep(WAIT_TIME)

    except KeyboardInterrupt:
        logging.info('Stoping...')

        screen.clear()
        screen.write('Stoping...', 0, 10)
        screen.show()

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        screen.clear()
        screen.write('ERROR!!!', 0, 10)
        screen.show()

    finally:
        shutdown()

