from selenium.webdriver.remote.webdriver import WebDriver

from src.selenium_facade.driver_facade import DriverFacade


class BaseView:
    """Base View.

    Use it to create new Views
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.driver_facade = DriverFacade(driver)
