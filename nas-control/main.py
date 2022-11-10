#!/bin/python3

from time import sleep
from signal import signal, SIGTERM

import RPi.GPIO as GPIO
from libs.log import logger as logging
from libs.oled import Oled
from libs.stats import hardware_stats, disk_stats, get_ip, get_temperature
from libs.fan import Fan
from libs.utils import run_command

GPIO_SWITCH = 23
GPIO_FAN = 18

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
        result = run_command(cmd)
        _, runlevel, _, _, _ = result.strip().split(' ')

        return True if int(runlevel) >= 3 and int(runlevel) <= 5 else False

    except:
        return False


def run_shutdown():
    logging.info('Requests Shutdown')
    run_command('poweroff')


def shutdown():
    GPIO.cleanup()

    logging.info('Ending script')

    if not Oled.check_available():
        logging.error('Pantalla no disponible, antes de apagar')

    else:
        display = Oled()
        display.write('Shutdown!', 0, 10)
        display.show()

    exit(0)


def handle_sigterm(_, __):
    shutdown()


if __name__ == '__main__':
    waiting_time = 1
    temperature = 100

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

                sleep(waiting_time)
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

            if is_boot_complete():  # standby
                waiting_time = 5
                stats = hardware_stats()
                disks = disk_stats(MOUNT_POINTS)
                ip = get_ip()
                temperature = get_temperature()

                line = 0
                x = 0
                for part, stat in stats:
                    stat = f'{stat:0.2f}%'

                    if len(stat) != 8:
                        stat = stat.rjust(8, ' ')

                    screen.write(
                        f'{part}:{stat}',
                        (x * 66) - 1,
                        OLED_LINES[line]
                    )
                    x += 1

                line += 1
                for disk, size, stat in disks:
                    if len(size) != 11:
                        size = size.rjust(11, ' ')

                    if len(stat) != 7:
                        stat = stat.rjust(7, ' ')

                    screen.write(disk, 0, OLED_LINES[line])
                    screen.write(size, 28, OLED_LINES[line])
                    screen.write(stat, 90, OLED_LINES[line])

                    line += 1

                screen.write(
                    f'IP: {ip}',
                    0,
                    OLED_LINES[line]
                )
                screen.write(
                    f'T: {temperature:0.2f}\'C',
                    87,
                    OLED_LINES[line]
                )

            else:
                try:
                    point = point + 1 if point < 4 else 0

                except NameError:
                    point = 0

                waiting_points = ''.join(['.' for _ in range(point)])
                text = f'Booting{waiting_points}'
                screen.write(text, 0, 10)

            fan.adjust(temperature)
            screen.show()
            sleep(waiting_time)

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

