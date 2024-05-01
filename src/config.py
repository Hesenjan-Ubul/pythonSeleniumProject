"""Global config."""

import inspect
import json
import os
import sys
from enum import StrEnum, auto
from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field, AnyHttpUrl, HttpUrl
from pydantic.fields import ModelField


class Environment(StrEnum):
    local = auto()
    development = auto()
    staging = auto()
    production = auto()
    ...


AppUrl = HttpUrl | Literal["https://demo.mahara.org/"]


class SeleniumTestsConfig(BaseSettings):
    """Main configuration."""

    ENVIRONMENT: Environment = Field(default=Environment.local,
                                     description="Environment in which the tests will run")
    LOCAL_URL: AnyHttpUrl = Field(default="https://demo.mahara.org/",
                                  description="Local URL, will only be used when Environment is set as 'local'")
    APP_URL: AppUrl = Field(default=None, description="Base URL of the app to test.")

    def gen_url_based_on_environment(cls, values: dict, field: ModelField):
        """Generate the URL based on the ENVIRONMENT value.

        Args:
            :param values: name-to-value mapping of any previously-validated fields.
            :param field: the field being validated.
        """

        environment: Environment = values["ENVIRONMENT"]
        if environment == Environment.local:
            return values["LOCAL_URL"]

        match environment:
            case Environment.development:
                domain = "company.com"
                app_url = f"development.{domain}"

            case Environment.staging:
                domain = "company.co"
                app_url = f"staging.{domain}"

            case Environment.production:
                domain = "company.io"
                app_url = f"platform.{domain}"

        url_schema = "https://"
        match field.name:
            case "APP_URL":
                return f"{url_schema}{app_url}"

    SELENIUM_PROVIDER: Literal["browserstack", "local"] = Field(
        default="local",
        description=(
            "Which infrastructure use to run tests.\n\n"
            "* ``local`` - triggers Selenium on your own machine\n"
            "* ``browserstack`` - run tests in BrowserStack infrastructure"
        ),
    )
    RETRY_NUMBER: int = Field(
        default=0,
        description="Number of failures before marking test as failed.\n\n**For local runs there are no retries**"
    )
    DELAY_BETWEEN_RETRIES_S: int = Field(default=5, description="Delay in seconds between each try of single test")
    LOCAL_ONLY_WHICH_BROWSERS_TO_USE: list[Literal["chrome", "firefox", "safari"]] = Field(
        default=["chrome"],
        description=(
            "Which browsers to use in local run.\n\n.. note::\n    "
            "You can specify multiple browsers, but take in account that in this case the tests will take **a lot** "
            "of time to complete"
        ),
    )


class PipelineMetaConfig(BaseSettings):
    """Env vars extracted from Gitlab pipeline.

    `Gitlab variables reference <https://docs.gitlab.com/ee/ci/variables/predefined_variables.html>`_
    """

    CI_COMMIT_SHA: str = Field(
        default="local",
        description="SHA of the commit to be used to create the test run name. Needs to be replaced with app's build hash"
    )
    CI_PIPELINE_ID: str = Field(default="local",
                                description="Gitlab pipeline id to be used to create the test run name")
    CI_COMMIT_BRANCH: str = Field(default="local", description="Gitlab commit branch name")
    CI_PIPELINE_URL: str = Field(description="Link to the Gitlab pipeline")
    PYTEST_ENVIRONMENT_SPECIFIC_COMMAND_ARGS: str = Field(
        default="",  # This is the bypass - empty string will add nothing to the CLI args.
        description=(
            "Pytest CLI arguments which are specific to the environment, against which we run E2E. "
            "You can use it for filtering tests. See ``.gitlab-ci.yml`` for more information"
        ),
        example="-m not skip_nightly",
    )


class UsersCredentialsConfig(BaseSettings):
    """Configuration for MAHARA_USER_credential for login"""

    # Configuration for MAHARA_USER_credential for login
    MAHARA_DEMO_USER_USERNAME: str = Field(description="Username which is used for login Mahara")
    MAHARA_DEMO_USER_PASSWORD: str = Field(description="Password which is used for login Mahara")


@lru_cache
def generate_dotenv_file():
    """Generate .env file for local development."""
    current_module = sys.modules[__name__]
    dotenv_lines = ["# Configuration for local run. Full description of variables you can find in ./src/config.py\n"]
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, BaseSettings) and not obj == BaseSettings:
            dotenv_lines.append(f"# {obj.__doc__}:".replace("\n", "\n#"))
            for key, model_field in obj.__fields__.items():
                default_value = json.dumps(model_field.default) if type(model_field.default) in [list,
                                                                                                 dict] else model_field.default
                dotenv_lines.append(f'{key}={default_value if not model_field.required else ""}')
    dotenv_file_path = ".env"
    if os.path.exists(dotenv_file_path):
        raise Exception(".env file already exist. Copypaste the info somewhere and delete it to proceed")

    with open(dotenv_file_path, "w") as fp:
        for line in dotenv_lines:
            fp.write(f"{line}\n")


def get_selenium_config() -> SeleniumTestsConfig:
    """Memoize fetching the config."""
    return SeleniumTestsConfig()


if __name__ == "__main__":
    generate_dotenv_file()
