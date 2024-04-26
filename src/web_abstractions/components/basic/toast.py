import logging
from typing import Optional

from selenium.common import TimeoutException

from src.selenium_facade.driver_facade import DriverFacade
from src.web_abstractions.components.basic.base import BaseBasicComponent
from src.web_abstractions.components.basic.clickable import ClickableComponent


class ToastComponent(BaseBasicComponent):
    @property
    def _toast_message(self) -> ClickableComponent:
        return ClickableComponent(driver_facade=self._driver_facade, element_query=self._element_query, find_by=self._find_by)

    def dismiss(self, timeout_s: Optional[float] = None):
        """Dismiss a toast message.

        Args:
            timeout_s: timeout in seconds to wait an element load.
        """
        self._toast_message.click(timeout_s=timeout_s)
        self._driver_facade.wait_for_element_not_present(element_query=self._element_query, find_by=self._find_by)

    @staticmethod
    def dismiss_all(driver_facade: DriverFacade):
        """Clear all toast messages in the screen (e.g. to avoid blocking clicking on an
        element)"""
        logging.info("Dismissing all toast messages")

        while True:
            try:
                ToastComponent(
                    driver_facade,
                    element_query="//*[contains(@data-testid, 'toast')]",
                ).dismiss(timeout_s=0.3)
            except Exception:
                logging.info("Dismissed all toast messages")
                break

    @staticmethod
    def has_error(driver_facade: DriverFacade, error_msg: Optional[str] = None):
        """Check if there is any error toast.

        Args:
            driver_facade: driver
            error_msg: Custom error message to be shown in the Exception

        Raises:
            Exception: if an error toast message is found.
        """

        driver_facade.raise_if_found(
            element_query='//*[@data-testid="toast-error"]',
            error_msg=error_msg or "Found a toast error with an error message",
        )

    def dismiss_with_error_handling(self, timeout_s: Optional[float] = None):
        """Dismiss a toast message, and check if there was any error toast in case of
        failure finding the message.

        Args:
            timeout_s: timeout in seconds to wait an element load.
        """

        try:
            self._driver_facade.wait_for_element_present(element_query="//*[@data-testid='toast-success']", timeout_s=timeout_s)
        except TimeoutException:
            ToastComponent.has_error(self._driver_facade)
        else:
            self.dismiss()
