import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class Oled:
  def __init__(self):
    RST = None

    DC = 23
    SPI_PORT = 0
    SPI_DEVICE = 0

    self.screen = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

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

  def write(self, text, x, y):
    self.draw.text((x, y), text, font=self.font, fill=255)

  def show(self):
    self.screen.image(self.image)
    self.screen.display()

  def clear(self):
    self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
