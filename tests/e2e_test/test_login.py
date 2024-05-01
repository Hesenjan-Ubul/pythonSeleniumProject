import pytest
from selenium.webdriver import Remote

from src.config import UsersCredentialsConfig
from src.web_abstractions.views.home import MaharaHomeView
from tests.predefined_steps.auth import log_the_user_in_steps


@pytest.mark.critical
def test_login_mahara(
        driver: Remote,
):
    user_config = UsersCredentialsConfig()

    # NOTE: TestRail test steps can be added before every test steps if TestRail is configured properly.
    log_the_user_in_steps(
        driver=driver,
        username=user_config.MAHARA_DEMO_USER_USERNAME,
        password=user_config.MAHARA_DEMO_USER_USERNAME
    )

    mahara_home = MaharaHomeView(driver)

    # NOTE: TestRail test steps can be added before every test steps if TestRail is configured properly.
    def _():
        mahara_home.driver_facade.wait_for_element_present(mahara_home.card_header_profile_block_xpath)

    # NOTE: TestRail test steps can be added before every test steps if TestRail is configured properly.
    def _():
        mahara_home.driver_facade.wait_for_element_present(mahara_home.list_group_item_xpath)
