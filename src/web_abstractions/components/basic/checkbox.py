from src.web_abstractions.components.basic.clickable import ClickableComponent


class CheckboxComponent(ClickableComponent):
    @staticmethod
    def label_query(label: str) -> str:
        """Generate a XPATH query with the checkbox label."""
        return f"//input[@name='{label}' and @type='checkbox']"

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
