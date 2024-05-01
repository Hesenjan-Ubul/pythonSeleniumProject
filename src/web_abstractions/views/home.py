from src.web_abstractions.components import ButtonComponent
from src.web_abstractions.views.base import BaseView


class MaharaHomeView(BaseView):
    """Index page of the CELUS app."""

    card_header_profile_block_xpath = "//h2[@class='card-header profile-block']"
    list_group_item_xpath = "//div[@id='groups']"
    show_account_menu_xpath = "//button[@title='Account menu']/child::span[contains(.,'Show account menu')]"
    logout_link_xpath = "//a[@id='logoutbutton']/child::span[.='Logout']"

    @property
    def show_account_menu(self) -> ButtonComponent:
        """The username dropdown."""
        return ButtonComponent(driver_facade=self.driver_facade, element_query=self.show_account_menu_xpath)

    @property
    def logout_link(self) -> ButtonComponent:
        """Logout button under the username dropdown."""
        return ButtonComponent(driver_facade=self.driver_facade, element_query=self.logout_link_xpath)

    @property
    def sign_in_again_button(self) -> ButtonComponent:
        """`Sign In Again` button after logged out the platform."""
        return ButtonComponent(driver_facade=self.driver_facade, element_query="//*[@data-testid='sign-in']")

    def sign_out(self):
        self.show_account_menu.click()
        self.logout_link.click()
