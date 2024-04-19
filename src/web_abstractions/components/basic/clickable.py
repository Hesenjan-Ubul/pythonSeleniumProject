from typing import Optional

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement

from src.constants import DEFAULT_TIMEOUT_S
from src.web_abstractions.components.basic.base import BaseBasicComponent


class ClickableComponent(BaseBasicComponent):
    def _get(self, timeout_s: Optional[float] = None) -> WebElement:
        """Finds an element by given path.

        Args:
            timeout_s: timeout in seconds to wait an element load.

        Returns:
            Matching element
        """
        return self._driver_facade.find_element(
            element_query=self._element_query, find_by=self._find_by, timeout_s=timeout_s or DEFAULT_TIMEOUT_S
        )

    def click(self, timeout_s: Optional[float] = None):
        """Click on the element.

        In case of ``StaleElementReferenceException`` recursively retries
        """
        element = self._get(timeout_s=timeout_s)
        try:
            self._driver_facade.generic_click(element)
        except StaleElementReferenceException:
            self.click()
