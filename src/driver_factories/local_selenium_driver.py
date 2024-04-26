from selenium.webdriver import Chrome, Firefox, Remote, Safari
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from src.config import get_selenium_config
from src.driver_factories.browser import get_browser_options
from src.driver_factories.driver_factory_base import DriverFactoryBase, DriverMeta


class LocalSeleniumDriverFactory(DriverFactoryBase):
    """"""

    config = get_selenium_config()
    parametrization_factors = config.LOCAL_ONLY_WHICH_BROWSERS_TO_USE

    @classmethod
    def create_driver(cls, parametrization_factor: dict, test_name: str, build_name: str) -> Remote:
        if parametrization_factor == "chrome":
            return Chrome(service=ChromeService(ChromeDriverManager().install()))
        elif parametrization_factor == "firefox":
            options = get_browser_options("firefox")
            return Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        elif parametrization_factor == "safari":
            # webdriver_manager doesn't support Safari.
            return Safari()
        raise NotImplementedError()

    @staticmethod
    def on_test_success(driver: Remote, reason: str = "Test passed") -> None:
        return

    @staticmethod
    def on_test_failure(driver: Remote, reason: str) -> None:
        return

    @staticmethod
    def get_driver_meta(driver: Remote) -> DriverMeta:
        return DriverMeta(name=driver.name, link_to_gui="n/a")
