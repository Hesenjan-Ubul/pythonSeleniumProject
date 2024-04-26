from selenium.webdriver.common.by import By

from src.selenium_facade.driver_facade import DriverFacade


class BaseBasicComponent:
    """Base Basic Component.

    Use it to create new Basic Components
    """

    def __init__(self, driver_facade: DriverFacade, element_query: str, find_by: str = By.XPATH):
        self._driver_facade = driver_facade
        self._element_query = element_query
        self._find_by = find_by

    @property
    def element_query(self):
        return self._element_query
