import os
import shutil
import uuid
from pathlib import Path
from typing import Callable, Generator

import pytest
from _pytest.fixtures import SubRequest
from retry import retry
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver import Remote

from src.config import get_selenium_config, PipelineMetaConfig
from src.constants import SCREENSHOTS_FAILURES_FOLDER, SCREENSHOTS_FOLDER
from src.driver_factories.driver_factory_base import DriverFactoryBase
from src.driver_factories.factories_map import DRIVER_FACTORY_MAP
from src.logger import logger
from src.selenium_facade.driver_facade import DriverFacade
from src.utils import load_dotenv_if_running_locally


def _create_folder(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def _create_screenshot_folder():
    path = Path(SCREENSHOTS_FOLDER).joinpath(SCREENSHOTS_FAILURES_FOLDER)
    if path.exists():
        shutil.rmtree(SCREENSHOTS_FOLDER)
    _create_folder(str(path))


def pytest_sessionstart():
    """*Not a fixture, but extension of pytest's hook*

    * If pytest is running on **local machine**: Loads data from ``.env``
    * Deletes all report filed from ``testrail-report-output`` dir
    * Creates ``screenshots`` dir
    """
    load_dotenv_if_running_locally()
    _create_screenshot_folder()


@pytest.fixture
def _build_name() -> str:
    """The build name to be used inside tests to distinguish different runs of tests."""
    ci_cd_config = PipelineMetaConfig()
    return f"{ci_cd_config.CI_COMMIT_BRANCH}_sha={ci_cd_config.CI_COMMIT_SHA[:8]}_pipeline={ci_cd_config.CI_PIPELINE_ID}"


def pytest_runtest_call(item):
    """*Not a fixture, but extension of pytest's hook*

    Adds ``retry`` decorator to each testcase.

    Does **not** add ``retry`` decorator if pytest is running on **local machine**.
    """
    selenium_config = get_selenium_config()
    if selenium_config.RETRY_NUMBER and selenium_config.SELENIUM_PROVIDER != "local":
        testfunction = item.obj
        # Add retry decorator for each test:
        item.obj = retry(tries=selenium_config.RETRY_NUMBER, delay=selenium_config.DELAY_BETWEEN_RETRIES_S)(
            testfunction)


@pytest.fixture
def gen_unique_name(_build_name) -> Callable[[str], str]:
    """Generates a unique resource name according with the test run config.

    Dummy example of usage:

    .. code-block:: python

       import json


       def test_example_of_gen_unique_name_fixture(driver, user_management,  gen_unique_name):
           user_management.create_the_user_and_do_log_in_steps(driver=driver)
           file_name = gen_unique_name(driver.name)
           json_str = json.dumps({"some": "content"})
           with open(f"{file_name}.json", "w") as outfile:
               outfile.write(json_str)
    """

    def wrapper(driver_name: str) -> str:
        return f"e2e_{_build_name}_driver={driver_name}_{str(uuid.uuid4())[:8]}".replace("/", "-")

    return wrapper


@pytest.fixture
def gen_unique_simple_resource_name(_build_name) -> Callable[[str], str]:
    """Generates a unique resource name according with the test run config.

    Dummy example of usage:

    .. code-block:: python

       import json

       def test_example_of_gen_unique_name_fixture(get_driver_logged_in, gen_unique_name):
           driver = get_driver_logged_in()
           file_name = gen_unique_name(driver.name)
           json_str = json.dumps({"some": "content"})
           with open(f"{file_name}.json", "w") as outfile:
               outfile.write(json_str)
    """

    def wrapper(driver_name: str) -> str:
        return f"E2E {driver_name} {str(uuid.uuid4())[:8]}"

    return wrapper


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # NOQA
    """*Not a fixture, but extension of pytest's hook*

    Make the test result available in fixtures:

    * ``request.node.rep_setup`` - will give you details about setup stage
     (the things which are happening in fixtures before the test itself)
    * ``request.node.rep_call`` - will give you details about results of the test itself

    Some useful information inside ``rep_setup`` and ``rep_call`` (they are inheriting the same class):

    * ``request.node.rep_setup.failed`` - bool, ``True`` if the setup/testcase failed
    * ``request.node.rep_setup.longrepr`` - Exception which occurred during the test execution/setup

    The method is copy-pasted from `this reference
    <https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures>`_
    """
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def _driver_factory() -> DriverFactoryBase:
    """Depending on ``SELENIUM_PROVIDER`` env var decides which driver factory to use

    Returns: DriverFactoryBase
    """
    selenium_config = get_selenium_config()
    return DRIVER_FACTORY_MAP[selenium_config.SELENIUM_PROVIDER]()


# Params because can't use fixture here
@pytest.fixture(params=DRIVER_FACTORY_MAP[get_selenium_config().SELENIUM_PROVIDER].parametrization_factors)
def driver(request: SubRequest, _build_name, _driver_factory: DriverFactoryBase) -> Generator[Remote, None, None]:
    """
    Gives you instance of Selenium ``WebDriver`` to use in the tests.

    Handles ``WebDriver``-related things:

    * Parametrizes tests for different browsers - see ``params`` parameter in ``pytest.fixture`` decorator above
    * Initializes ``WebDriver``
    * Yields ``WebDriver`` to be used further
    * Does TearDown for ``WebDriver`` - sends results to Remote Driver provider (success/failure), closes connection to
    ``WebDriver``
    """
    # This is done before each test case:
    driver_to_yield: Remote = _driver_factory.create_driver(
        parametrization_factor=request.param, test_name=request.node.name, build_name=_build_name
    )
    # Set the driver meta to make it available in other fixtures:
    setattr(request.node, "driver_meta", _driver_factory.get_driver_meta(driver_to_yield))
    driver_to_yield.maximize_window()

    # Here the driver is passed to the test case:
    yield driver_to_yield

    # After each test case (no matter failure or success), this code is executed:
    if request.node.rep_setup.failed or request.node.rep_call.failed:
        driver_facade = DriverFacade(driver_to_yield)
        try:
            driver_facade.screenshot(filename=request.node.name, extra_path=SCREENSHOTS_FAILURES_FOLDER)
        except InvalidSessionIdException:
            logger.exception("Cannot take a screenshot")

        _driver_factory.on_test_failure(driver_to_yield, "Test setup failed, see pytest logs in gitlab")
    elif request.node.rep_setup.passed:
        _driver_factory.on_test_success(driver_to_yield)

    driver_to_yield.close()
    # Safari when running locally doesn't need `quit` call:
    selenium_config = get_selenium_config()
    if selenium_config.SELENIUM_PROVIDER == "local" and driver_to_yield.name == "Safari":
        return
    driver_to_yield.quit()


@pytest.fixture()
def data_dir_absolute_path() -> str:
    """Return the absolute path of 'tests/data' directory of the e2e automated
    project."""

    tests_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(tests_dir, "data")
    return data_dir
