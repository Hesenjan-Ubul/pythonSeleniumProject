from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver


class DriverMeta(BaseModel):
    name: str
    link_to_gui: str


class DriverFactoryBase(ABC):
    # parametrization_factors - list of Any to be used as `params` parameter of pytest fixture.
    # Each entity of it will be passed to create_driver method
    parametrization_factors: list

    @staticmethod
    @abstractmethod
    def create_driver(parametrization_factor: Any, test_name: str, build_name: str) -> RemoteWebDriver:
        ...

    @staticmethod
    @abstractmethod
    def on_test_failure(driver, reason):
        ...

    @staticmethod
    @abstractmethod
    def on_test_success(driver):
        ...

    @staticmethod
    @abstractmethod
    def get_driver_meta(driver) -> DriverMeta:
        ...
