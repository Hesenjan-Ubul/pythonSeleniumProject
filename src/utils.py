import os


def load_dotenv_if_running_locally():
    # If the expression equals true, the tests are run in local machine
    if not os.getenv("CI_PIPELINE_ID"):
        # Import here on purpose to make CI/CD pipeline independent of dev dependency:
        from dotenv import load_dotenv  # NOQA

        load_dotenv()
