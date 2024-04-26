from typing import Literal

from selenium import webdriver
from selenium.webdriver.safari.options import Options as SafariOptions

BrowserName = Literal["chrome", "firefox", "safari", "edge"]

FF_SETTINGS: dict[str, bool | str | int] = {
    "browser.download.useDownloadDir": True,
    "browser.download.alwaysOpenPanel": False,
    "browser.helperApps.neverAsk.saveToDisk": "application/pdf",
    "browser.download.manager.quitBehavior": 2,
    "pdfjs.disabled": True,
}


def get_browser_options(browser: BrowserName):
    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        for key, value in FF_SETTINGS.items():
            options.set_preference(key, value)

        return options

    switcher = {
        "chrome": webdriver.ChromeOptions(),
        "safari": SafariOptions(),
        "edge": webdriver.EdgeOptions(),
    }
    return switcher.get(browser, switcher["chrome"])
