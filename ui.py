import buttons
import display
import machine

NAMED_BUTTONS = [
    (buttons.BTN_A, 'a'),
    (buttons.BTN_B, 'b'),
    (buttons.BTN_START, 'start'),
    (buttons.BTN_SELECT, 'SELECT'),
]

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

        for button, name in NAMED_BUTTONS:
            self._add_button_event_handler(button, name)

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

    def _add_button_event_handler(self, button, name):
        press_fn_name = "on_press_%s" % name
        release_fn_name = "on_release_%s" % name
        def on_button(pressed):
            if self.active_view:
                if pressed:
                    getattr(self.active_view, press_fn_name)()
                else:
                    getattr(self.active_view, release_fn_name)()

                display.flush()  # TODO: only flush if a screen update happened

        buttons.attach(button, on_button)


    def set_view(self, view):
        self.active_view = view
        view.activate()
        view.draw()
        display.flush()


class Focusable:
    focusable = True
    help_text = ""

    def __init__(self):
        self.focused = False
        super().__init__()

    def on_move(self, button):
        pass

    def _hide_help(self):
        if self.help_text:
            display.drawRect(
                0, display.height() - 16, display.width(), 16, True, 0xffffff
            )

    def _show_help(self):
        if self.help_text:
            display.drawText(
                0, display.height() - 16, self.help_text, 0x000000
            )

    def draw(self):
        if self.focused:
            self._show_help()

    def on_blur(self, button=None):
        self.focused = False
        self.draw()
        self._hide_help()

    def on_focus(self, button=None):
        self.focused = True
        self.draw()


def _add_focusable_button_method(name):
    def do_nothing(self):
        pass

    setattr(Focusable, name, do_nothing)


for button, name in NAMED_BUTTONS:
    _add_focusable_button_method("on_press_%s" % name)
    _add_focusable_button_method("on_release_%s" % name)


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

    def draw(self):
        for widget in self.widgets:
            widget.draw()


def _add_widget_container_button_method(name):
    def delegate_to_active_widget(self):
        if self.active_widget:
            getattr(self.active_widget, name)()

    setattr(WidgetContainer, name, delegate_to_active_widget)


for button, name in NAMED_BUTTONS:
    _add_widget_container_button_method("on_press_%s" % name)
    _add_widget_container_button_method("on_release_%s" % name)


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
        self.label_width = display.getTextWidth(self.label)
        self.label_height = display.getTextHeight(self.label)
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
        super().draw()


class NumberInput(Focusable, Widget):
    help_text = "hold A and move up / down to change value"

    def __init__(self, label, value, x, y, min_value=None, max_value=None, on_change=None):
        super().__init__()
        self.label = label
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.x = x
        self.y = y
        self.height = 16
        self.label_width = display.getTextWidth(self.label)
        self.value_width = display.getTextWidth(str(self.value))
        self.holding_button = False

        self.on_change = on_change

    def on_press_a(self):
        self.holding_button = True

    def on_release_a(self):
        self.holding_button = False

    def on_move(self, button):
        if self.holding_button:
            if button == buttons.BTN_UP:
                new_value = self.value + 1
                if self.max_value is not None and new_value > self.max_value:
                    new_value = self.max_value
            elif button == buttons.BTN_DOWN:
                new_value = self.value - 1
                if self.min_value is not None and new_value < self.min_value:
                    new_value = self.min_value

            if new_value != self.value:
                self.value = new_value
                self.value_width = display.getTextWidth(str(self.value))
                self.draw()
                if self.on_change:
                    self.on_change(self.value)
            return True

    def draw(self):
        display.drawText(self.x, self.y, self.label, 0x000000)
        if self.focused:
            display.drawRect(
                self.x + self.label_width + 5, self.y, 32, self.height, True, 0x0fffff
            )
        else:
            display.drawRect(
                self.x + self.label_width + 5, self.y, 32, self.height, True, 0xffffff
            )

        display.drawRect(
            self.x + self.label_width + 5, self.y, 32, self.height, False, 0x000000
        )
        right_x = self.x + self.label_width + 5 + 32
        display.drawText(right_x - self.value_width - 2, self.y, str(self.value), 0x000000)
        super().draw()