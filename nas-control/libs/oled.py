from Adafruit_SSD1306 import SSD1306_128_32 as Adafruit_oled
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from libs.utils import run_command
from libs.log import logger as logging


class Oled:
  def __init__(self) -> None:
    RST = None

    self.screen = Adafruit_oled(rst=RST)

    self.screen.begin()

    self.screen.clear()
    self.screen.display()

    self.width = self.screen.width
    self.height = self.screen.height
    self.image = Image.new("1", (self.width, self.height))

    self.draw = ImageDraw.Draw(self.image)

    self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    # self.font = ImageFont.load_default()
    self.font = ImageFont.truetype('Silkscreen-Regular.ttf', size=8)

  @staticmethod
  def check_available() -> bool:
    cmd ='ls /dev/i2c*'

    try:
      run_command(cmd)
      return True

    except:
      return False

  def write(self, text:str, x:int, y:int) -> None:
    self.draw.text((x, y), text, font=self.font, fill=255)

  def show(self) -> None:
    self.screen.image(self.image)
    self.screen.display()

  def clear(self) -> None:
    self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
