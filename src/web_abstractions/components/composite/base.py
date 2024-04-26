from src.selenium_facade.driver_facade import DriverFacade


class BaseCompositeComponent:
    """Base Composite Component.

    Use it to create new Composite Components
    """

    def __init__(self, driver_facade: DriverFacade):
        self._driver_facade = driver_facade
