from libs.log import logger as logging

from RPi.GPIO import setup, OUT, LOW, PWM

PWM_FREQ = 100
FAN_OFF = 0
FAN_LOW = 50
FAN_HIGH = 100

OFF_TEMP = 23
MIN_TEMP = 30
MAX_TEMP = 50


class Fan:
    def __init__(self, pin:int) -> None:
        setup(pin, OUT, initial=LOW)
        self.__instance_pwm__ = PWM(pin, PWM_FREQ)

    def adjust(self, temperature:float) -> None:
        if temperature <= OFF_TEMP:
            dutyCycle = FAN_OFF

        elif temperature > OFF_TEMP and temperature < MAX_TEMP:
            dutyCycle = MIN_TEMP

        else:
            dutyCycle = FAN_HIGH

        logging.info('Temperature: %s \'C' % temperature)
        logging.info('Duty Cycle: %s' % dutyCycle)
        self.__instance_pwm__.start(dutyCycle)
