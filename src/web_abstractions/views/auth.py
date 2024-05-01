from selenium.webdriver.common.by import By

from src.web_abstractions.components import ButtonComponent, InputComponent
from src.web_abstractions.views.base import BaseView


class SignInView(BaseView):
    """Keycloak page with the login form.

    You can use it in fixtures to log the user in
    """

    @property
    def _login_button(self) -> ButtonComponent:
        return ButtonComponent(driver_facade=self.driver_facade, element_query="#login_submit", find_by=By.CSS_SELECTOR)

    @property
    def _username_input(self) -> InputComponent:
        return InputComponent(driver_facade=self.driver_facade, element_query="#login_login_username",
                              find_by=By.CSS_SELECTOR)

    @property
    def _password_input(self) -> InputComponent:
        return InputComponent(driver_facade=self.driver_facade, element_query="#login_login_password",
                              find_by=By.CSS_SELECTOR)

    def login_button_click(self):
        """Click on the submit bottom of the login form.

        After the click it checks:

        * if login was successful
        * if ``webapp_api_token`` cookie was assigned
        """
        self._login_button.click()
        # Check if showed any login error message
        self.driver_facade.raise_if_found(
            "kc-feedback-text",
            find_by=By.CLASS_NAME,
            error_msg="Login failed",
        )
        self.driver_facade.wait_for_cookie_present("webapp_api_token")

    def fill_username_and_password(self, username: str, password: str):
        """Helper to fill the login form."""
        self._username_input.fill(value=username)
        self._password_input.fill(value=password)

    @property
    def register_link(self) -> ButtonComponent:
        """Register button in the Mahara Demo login page."""
        return ButtonComponent(driver_facade=self.driver_facade, element_query="Register", find_by=By.LINK_TEXT)

    @property
    def lost_username_password_link(self) -> ButtonComponent:
        """Lost username/password link in the Mahara Demo login page."""
        return ButtonComponent(driver_facade=self.driver_facade, element_query="//*[text()='Lost username / password']",
                               find_by=By.LINK_TEXT)
