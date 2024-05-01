from typing import Optional

from retry import retry
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Remote

from src.config import get_selenium_config
from src.web_abstractions.views.auth import SignInView


@retry(exceptions=(TimeoutException, WebDriverException), tries=4, delay=1, backoff=2)
def log_the_user_in_steps(
        driver: Remote,
        username: str,
        password: str,
        url: Optional[str] = None,
):
    config = get_selenium_config()
    mahara_demo_url = config.APP_URL if config.APP_URL else config.LOCAL_URL
    target_url = url or mahara_demo_url

    # NOTE: TestRail test steps can be added before every test steps if TestRail is configured properly.
    def _():
        driver.get(target_url)

    sign_in_form = SignInView(driver)

    # NOTE: TestRail test steps can be added before every test steps if TestRail is configured properly.
    def _():
        sign_in_form.fill_username_and_password(username=username, password=password)

    # NOTE: TestRail test steps can be added before every test steps if TestRail is configured properly.
    def _():
        sign_in_form.login_button_click()
