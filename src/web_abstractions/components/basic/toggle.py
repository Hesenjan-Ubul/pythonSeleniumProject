from src.web_abstractions.components.basic.clickable import ClickableComponent


class ToggleComponent(ClickableComponent):
    def check(self):
        """Set the value as true for the element."""
        e = self._get()
        if not e.is_selected():
            self.click()

    def uncheck(self):
        """Set the value as false for the element."""
        e = self._get()
        if e.is_selected():
            self.click()

    def toggle(self, activate: bool):
        """Toggle the value for the element."""
        if activate:
            self.check()
        else:
            self.uncheck()
