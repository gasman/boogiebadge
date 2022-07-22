import buttons
import display
import machine

class Controller:
    def __init__(self, timer_id=0):
        self.timer = machine.Timer(timer_id)
        self.current_button = None
        self.ticks_since_press = 0
        self.debounce_ticks = 5
        self.active_view = None

        def tick(t):
            if self.current_button is not None:
                self.ticks_since_press += 1
                if self.ticks_since_press > self.debounce_ticks and self.active_view:
                    self.active_view.on_move(self.current_button)

        self.timer.init(period=100, callback=tick)

        for button in (buttons.BTN_UP, buttons.BTN_DOWN, buttons.BTN_LEFT, buttons.BTN_RIGHT):
            self._add_joystick_event_handler(button)

        def on_button_a(pressed):
            if self.active_view:
                if pressed:
                    self.active_view.on_press_a()
                else:
                    self.active_view.on_release_a()

                display.flush()  # TODO: only flush if a screen update happened

        buttons.attach(buttons.BTN_A, on_button_a)

        def on_button_b(pressed):
            if self.active_view:
                if pressed:
                    self.active_view.on_press_b()
                else:
                    self.active_view.on_release_b()

                display.flush()  # TODO: only flush if a screen update happened

        buttons.attach(buttons.BTN_B, on_button_b)

    def _add_joystick_event_handler(self, button):
        def event_handler(pressed):
            if pressed:
                self.current_button = button
                self.ticks_since_press = 0
                if self.active_view:
                    self.active_view.on_move(self.current_button)
            elif self.current_button == button:
                self.current_button = None

            display.flush()  # TODO: only flush if a screen update happened

        buttons.attach(button, event_handler)

    def set_view(self, view):
        self.active_view = view
        view.activate()
        view.draw()
        display.flush()


class Focusable:
    focusable = True

    def __init__(self):
        self.focused = False
        super().__init__()

    def on_move(self, button):
        pass

    def on_press_a(self):
        pass

    def on_release_a(self):
        pass

    def on_press_b(self):
        pass

    def on_release_b(self):
        pass

    def on_blur(self, button):
        self.focused = False
        self.draw()

    def on_focus(self, button):
        self.focused = True
        self.draw()


class WidgetContainer:
    widgets = []
    wrap_focus = False

    def __init__(self):
        if self.widgets:
            self.active_widget = self.widgets[0]
            # TODO: updating active_widget_index if the widgets list is modified
            self.active_widget_index = 0
        else:
            self.active_widget = None
            self.active_widget_index = None

    def get_next_focusable_widget(self):
        index = self.active_widget_index
        checked_count = 0
        while (checked_count < len(self.widgets)):
            index += 1
            if index >= len(self.widgets):
                if self.wrap_focus:
                    index = 0
                else:
                    return None, None

            widget = self.widgets[index]
            if widget.focusable:
                return index, widget

        return None, None

    def get_previous_focusable_widget(self):
        index = self.active_widget_index
        checked_count = 0
        while (checked_count < len(self.widgets)):
            index -= 1
            if index < 0:
                if self.wrap_focus:
                    index = len(self.widgets) - 1
                else:
                    return None, None

            widget = self.widgets[index]
            if widget.focusable:
                return index, widget

        return None, None

    def on_move(self, button):
        if self.active_widget:
            keep_focus = self.active_widget.on_move(button)
            if keep_focus:
                return True
            else:
                self.active_widget.on_blur(button)
                if button in (buttons.BTN_UP, buttons.BTN_LEFT):
                    self.active_widget_index, self.active_widget = self.get_previous_focusable_widget()
                else:
                    self.active_widget_index, self.active_widget = self.get_next_focusable_widget()

                if self.active_widget:
                    self.active_widget.on_focus(button)
                    return True
                else:
                    return False

    def on_press_a(self):
        if self.active_widget:
            self.active_widget.on_press_a()

    def on_release_a(self):
        if self.active_widget:
            self.active_widget.on_release_a()

    def on_press_b(self):
        if self.active_widget:
            self.active_widget.on_press_b()

    def on_release_b(self):
        if self.active_widget:
            self.active_widget.on_release_b()

    def draw(self):
        for widget in self.widgets:
            widget.draw()


class View(WidgetContainer):
    wrap_focus = True

    def activate(self):
        pass

    def deactivate(self):
        pass

    def draw(self):
        display.drawFill(display.WHITE)
        super().draw()


class Widget:
    focusable = False

    def draw(self):
        pass


class Button(Focusable, Widget):
    def __init__(self, label, x, y):
        super().__init__()
        self.label = label
        self.x = x
        self.y = y
        self.width = 32
        self.height = 16
        self.label_width = display.getTextWidth(self.label)
        self.label_height = display.getTextHeight(self.label)

    def set_label(self, text):
        self.label = text
        self.draw()

    def draw(self):
        if self.focused:
            display.drawRect(self.x, self.y, self.width, self.height, True, 0x000000)
            display.drawText(
                self.x + int(self.width / 2 - self.label_width / 2),
                self.y + int(self.height / 2 - self.label_height / 2),
                self.label,
                0xffffff,
            )
        else:
            display.drawRect(self.x, self.y, self.width, self.height, True, 0xffffff)
            display.drawRect(self.x, self.y, self.width, self.height, False, 0x000000)
            display.drawText(
                self.x + int(self.width / 2 - self.label_width / 2),
                self.y + int(self.height / 2 - self.label_height / 2),
                self.label,
                0x000000,
            )
