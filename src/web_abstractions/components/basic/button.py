from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webelement import WebElement

from src.web_abstractions.components.basic.base import BaseBasicComponent


class ButtonComponent(BaseBasicComponent):
    @staticmethod
    def label_query(label: str) -> str:
        """Generate a ``xpath`` query with the button label"""
        return f"//*[text()='{label}']/ancestor::button"

    def get(self) -> WebElement:
        """Find an element by a query."""
        return self._driver_facade.find_element(element_query=self._element_query, find_by=self._find_by)

    def click(self):
        """Waits for the button to be enabled and clicks on it.

        In case of ``StaleElementReferenceException`` recursively retries
        """
        element = self.get()
        try:
            self._driver_facade.wait_for_element_enabled(element)
            element.click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            return self.click()
