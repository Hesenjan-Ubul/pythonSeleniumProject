from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.remote.webelement import WebElement

from src.web_abstractions.components.basic.base import BaseBasicComponent


class InputComponent(BaseBasicComponent):
    def __init__(self, sleep_time_after: float = 0.3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep_time_after = sleep_time_after

    def get(self) -> WebElement:
        return self._driver_facade.find_element(element_query=self._element_query, find_by=self._find_by)

    def fill(self, value: str):
        element = self.get()
        self.clear_input_field()
        element.send_keys(value)

        sleep(self.sleep_time_after)  # Need to wait a bit after typing so the UI propagates the value

    def clear_input_field(self):
        """Use this method to clear the input field"""

        input_field = self.get()
        value = input_field.get_attribute("value")
        if value:
            input_field.send_keys(Keys.BACKSPACE * len(value))
