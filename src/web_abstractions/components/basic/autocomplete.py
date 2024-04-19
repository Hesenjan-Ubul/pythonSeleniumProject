from time import sleep
from typing import Optional

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from src.web_abstractions.components.basic.base import BaseBasicComponent


class AutocompleteComponent(BaseBasicComponent):
    def __init__(self, sleep_time_before_click: Optional[float] = None, sleep_time_before_opening: Optional[float] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep_time_before_click = sleep_time_before_click
        self.sleep_time_before_opening = sleep_time_before_opening

    def set_value(self, value: str):
        if self.sleep_time_before_opening:
            # NOTE: for some cases it infills the data unless there is this wait
            sleep(self.sleep_time_before_opening)

        element: WebElement = self._driver_facade.fill_input_box(element_query=self._element_query, find_by=self._find_by, value=value)

        if self.sleep_time_before_click:
            # NOTE: for some cases when the data is too big on the backend, we have to wait until it is loaded
            sleep(self.sleep_time_before_click)

        element.send_keys(Keys.ENTER)
