import display

class Button:
    def __init__(self, label, x, y):
        self.label = label
        self.x = x
        self.y = y
        self.width = 32
        self.height = 16
        self.label_width = display.getTextWidth(self.label)
        self.label_height = display.getTextHeight(self.label)

    def draw(self):
        display.drawRect(self.x, self.y, self.width, self.height, False, 0x000000)
        display.drawText(
            self.x + int(self.width / 2 - self.label_width / 2),
            self.y + int(self.height / 2 - self.label_height / 2),
            self.label,
            0x000000,
        )
