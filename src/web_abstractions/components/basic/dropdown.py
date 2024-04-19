from time import sleep

from selenium.common import TimeoutException

from src.constants import DROPDOWN_OPTIONS_TIMEOUT_S
from src.web_abstractions.components import ButtonComponent
from src.web_abstractions.components.basic.base import BaseBasicComponent


class DropdownComponent(BaseBasicComponent):
    def get(self) -> ButtonComponent:
        return ButtonComponent(driver_facade=self._driver_facade, element_query=self._element_query, find_by=self._find_by)

    def select_option(self, option: str):
        element = self.get()
        element.click()
        sleep(2)  # Trying to not have the dropdown vanishing value

        element_query_with_data_value = f'//*[@data-value="{option}"]'
        element_query_with_title = f'//*[@title="{option}"]'
        try:
            self._driver_facade.find_element(element_query_with_data_value, timeout_s=DROPDOWN_OPTIONS_TIMEOUT_S).click()
            sleep(3)  # Trying to not have the dropdown vanishing value
            # Allow the component to collapse after selecting
            self._driver_facade.wait_for_element_not_present(element_query_with_data_value)
        except TimeoutException:
            self._driver_facade.find_element(element_query_with_title).click()
            sleep(3)
