import json
import os
import re
import time
from pathlib import Path
from re import Pattern
from typing import Any, Optional, Type, Union
from urllib.parse import unquote, urlencode, urljoin, urlsplit

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from src.constants import DEFAULT_TIMEOUT_S, SCREENSHOTS_FOLDER


class DriverFacade:
    """Facade to ease the usage of the driver.

    Preferably
    `use naming from Selenium IDE <https://www.selenium.dev/selenium-ide/docs/en/api/commands>`_
    when creating new methods. All the low-level Selenium stuff should be implemented here
    """

    # Selenium IDE commands reference: https://www.selenium.dev/selenium-ide/docs/en/api/commands
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait_for_element_present(self, element_query: str, find_by: str = By.XPATH, timeout_s: Optional[float] = None):
        """Wait for a target element to be present on the page."""
        timeout = timeout_s or DEFAULT_TIMEOUT_S
        WebDriverWait(self.driver, timeout=timeout).until(
            ec.presence_of_element_located((find_by, element_query)),
            f'could not detect element with: "[{find_by}] `{element_query}`"',
        )

    def wait_for_cookie_present(self, cookie_name: str, timeout_s: float = DEFAULT_TIMEOUT_S) -> bool:
        """Wait for a target cookie to be present."""
        start_time = time.time()
        # There is no built-in way in Selenium to wait for the cookie
        while True:
            if time.time() - start_time > timeout_s:
                raise Exception(f"Cookie `{cookie_name}` was not found")
            if not self.driver.get_cookie(cookie_name):
                time.sleep(0.1)
                continue
            return True

    def wait_for_element_not_present(self, element_query: str, find_by: str = By.XPATH, timeout_s: float = DEFAULT_TIMEOUT_S):
        """Wait for a target element to not be present on the page."""
        WebDriverWait(self.driver, timeout_s).until(
            ec.invisibility_of_element_located((find_by, element_query)), f"element {element_query} is still present."
        )

    def wait_for_element_enabled(self, element: WebElement, timeout_s: float = DEFAULT_TIMEOUT_S):
        WebDriverWait(self.driver, timeout_s).until(
            lambda _: not element.get_property("disabled"),
            "element is not enabled",
        )

    def fill_input_box(self, element_query: str, find_by: str, value: str) -> WebElement:
        element: WebElement = self.find_element(element_query=element_query, find_by=find_by)
        element.send_keys(Keys.BACKSPACE * len(element.get_attribute("value") or ""))
        element.send_keys(value)
        time.sleep(0.3)  # Need to wait a bit after typing so the UI propagates the value

        return element

    def find_element(
        self,
        element_query: str,
        find_by: str = By.XPATH,
        parent: Optional[WebElement] = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        error_msg: Optional[str] = None,
    ) -> WebElement:
        """Finds an element by given path.

        It waits for it to be loaded and throws an error when not.

        Args:
            element_query: query for finding the element.
            find_by: type of query. Defaults to By.XPATH.
            parent: If set, it starts searching from given element.
            timeout_s: timeout in seconds to wait an element load.
            error_msg: custom error message to be shown.

        Returns:
            The element corresponding to that query.
        """

        return self._find(  # type: ignore[return-value]
            element_query=element_query,
            find_by=find_by,
            parent=parent,
            multiple=False,
            timeout_s=timeout_s,
            error_msg=error_msg,
        )

    def find_multiple(
        self,
        element_query: str,
        find_by: str = By.XPATH,
        parent: Optional[WebElement] = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        error_msg: Optional[str] = None,
    ) -> list[WebElement]:
        """Finds multiple elements by given path.

        It waits for it to be loaded and throws an error when not.

        Args:
            element_query: query for finding the element.
            find_by: type of query. Defaults to By.XPATH.
            parent: If set, it starts searching from given element.
            timeout_s: timeout in seconds to wait an element load.
            error_msg: custom error message to be shown.

        Returns:
            All elements corresponding to that query.
        """

        return self._find(  # type: ignore[return-value]
            element_query=element_query,
            find_by=find_by,
            parent=parent,
            multiple=True,
            timeout_s=timeout_s,
            error_msg=error_msg,
        )

    def _find(
        self,
        element_query: str,
        find_by: str = By.XPATH,
        parent: Optional[WebElement] = None,
        multiple: bool = False,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        error_msg: Optional[str] = None,
    ) -> WebElement | list[WebElement]:
        """Finds an element by given path.

        It waits for it to be loaded and throws an error when not.

        Args:
            element_query: query for finding the element.
            find_by: type of query. Defaults to By.XPATH.
            parent: If set, it starts searching from given element.
            multiple: whether it searches for multiple elements
            timeout_s: timeout in seconds to wait an element load.
            error_msg: custom error message to be shown.

        Returns:
            The element corresponding to that path.
        """
        self.wait_for_element_present(element_query=element_query, find_by=find_by, timeout_s=timeout_s)

        initiator: WebDriver | WebElement = self.driver if parent is None else parent

        if not multiple:
            result: WebElement = initiator.find_element(find_by, element_query)
        else:
            result: list[WebElement] = initiator.find_elements(find_by, element_query)  # type: ignore[no-redef]

        assert result, error_msg or f'element "[{find_by}] {element_query}" not found'

        return result

    def count_elements_no_assert(self, element_query: str, find_by: str = By.XPATH, parent: Optional[WebElement] = None) -> int:
        """Counts number of elements by a given query. . warning:: This does not wait for any condition nor fails,
        so use it only associated with a pre-condition and an assertion

        Args:
            element_query: query for finding the element.
            find_by: type of query. Defaults to By.XPATH.
            parent: If set, it starts searching from given element.

        Returns:
            The number of elements corresponding to that path.
        """
        initiator: Union[WebDriver, WebElement] = self.driver if parent is None else parent
        result = initiator.find_elements(find_by, element_query)
        return len(result)

    def drag_and_drop_to_object(
        self, element_to_be_dragged: WebElement, element_to_drag_to: WebElement, offset_x: int = 0, offset_y: int = 0
    ):
        """Drags an element and drops it on another element."""
        this_dir_path = os.path.dirname(os.path.abspath(__file__))
        with open(f"{this_dir_path}/drag_n_drop.js", "r") as f:
            javascript = f.read()
        self.driver.execute_script(javascript, element_to_be_dragged, element_to_drag_to, offset_x, offset_y)

    def raise_if_found(
        self,
        element_query: str,
        find_by: str = By.XPATH,
        error_msg: Optional[str] = None,
        exc: Type[BaseException] = Exception,
    ):
        """Raises an exception if the element is found. For example, this is useful for
        asserting that an error message was not showed.

        Args:
            element_query: query for finding the element.
            find_by: type of query. Defaults to By.XPATH.
            error_msg: custom error message to be shown.
            exc: Exception to be raised
        """
        try:
            self.driver.find_element(find_by, element_query)
            raise exc(error_msg)
        except NoSuchElementException:
            pass

    def screenshot(self, filename: str = "screenshot", extra_path: str = ""):
        path = Path(SCREENSHOTS_FOLDER).joinpath(extra_path, f"{filename}.png")
        self.driver.save_screenshot(str(path))

    def generic_click(self, element: WebElement):
        """This can be used with any clickable element."""
        try:
            self.driver.execute_script("arguments[0].click();", element)
        except Exception:
            element.click()

    def get_current_url(
        self, wait_for_pattern: Optional[Pattern] = None, timeout_s: float = DEFAULT_TIMEOUT_S, error_msg: Optional[str] = None
    ) -> str:
        """Get current URL after optionally waiting for a pattern on it. Useful to
        extract variables and IDs from the URL after ensuring that you are already at
        the right place.

        Args:
            wait_for_pattern: Optional pattern to wait for
            timeout_s: timeout in seconds to wait for the pattern to emerge
            error_msg: error message on timeout

        Returns: the URL
        """

        if not wait_for_pattern:
            return self.driver.current_url

        start = time.time()
        while time.time() - start < timeout_s:
            if len(re.findall(wait_for_pattern, self.driver.current_url)) == 1:
                return self.driver.current_url
            time.sleep(0.1)

        error_msg = error_msg or f'pattern "{wait_for_pattern}" did not match URL {self.driver.current_url}'
        assert re.findall(wait_for_pattern, self.driver.current_url) is not None, error_msg
        return self.driver.current_url

    def get_auth_token(self) -> str:
        """
        Get the current Auth token
        Returns: the Auth token string
        """
        cookie: dict[str, Any] | None = self.driver.get_cookie("webapp_api_token")
        if not cookie:
            return ""

        return json.loads(unquote(cookie["value"]))["access_token"]

    def build_url(self, *paths: str, query: Optional[dict[str, str]] = None, hostname: Optional[str] = None):
        """
        Builds a URL using path parts and the current hostname
        Args:
            paths: pieces of the path
            query: optional dict with the query arguments
            hostname: optional hostname, if not provided, will use current

        Returns: the URL with current hostname and path
        """
        if hostname is None:
            url_parts = urlsplit(self.driver.current_url)
            hostname = f'{url_parts.scheme or "https"}://{url_parts.netloc}'
        path = "/".join([p.strip("/") for p in paths])
        query_str: str = f"?{urlencode(query)}" if query else ""
        return urljoin(hostname.strip("/"), path + query_str)

    def scroll(self, x: int = 0, y: int | str = "document.body.scrollHeight"):
        """Scroll page to a point in the page."""
        self.driver.execute_script(f"window.scrollTo({x}, {y})")

    def focus_on_new_tab(self, close_previous: bool, tab_index: int = 0):
        """Switch the focus to a new tab, closing the previous tab if specified."""
        wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT_S)
        wait.until(ec.number_of_windows_to_be(tab_index + 1))
        if close_previous:
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def switch_to_iframe(self, element_query: str, find_by: str = By.XPATH, timeout_s: float = DEFAULT_TIMEOUT_S):
        """Switch to the iFrame with the specified query and timeout."""
        iframe: WebElement = self.find_element(element_query=element_query, find_by=find_by, timeout_s=timeout_s)
        self.driver.switch_to.frame(iframe)

    def navigate_to_endpoint(self, endpoint: str):
        """Navigate directly to a specific endpoint."""
        url = urljoin(self.driver.current_url, endpoint)
        self.driver.get(url)
