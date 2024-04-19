import json
import os
import shutil
import uuid
from typing import Optional, Tuple

import requests
from _pytest.fixtures import SubRequest

from src.config import PipelineMetaConfig
from src.report.models import ReportModel


def get_report_dir():
    pipeline_config = PipelineMetaConfig()
    return f"./testrail-report-output/{pipeline_config.CI_PIPELINE_ID}"


def combine_all_reports_files(default_report_dir: Optional[str] = None) -> ReportModel:
    report_dir = default_report_dir or get_report_dir()
    report_combined: dict = {"cases": []}
    for filename in os.listdir(report_dir):
        with open(f"{report_dir}/{filename}", "r") as f:
            file_data = json.load(f)
            report_combined["run"] = file_data["run"]
            report_combined["cases"] += file_data["cases"]

    return ReportModel(
        run=report_combined["run"],
        cases=sorted(
            report_combined["cases"],
            key=lambda case: case["test_result"]["status_id"],
        ),
    )


def delete_all_report_files() -> None:
    report_dir = get_report_dir()
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir)


def save_report_to_file(report: ReportModel):
    report_dir = get_report_dir()
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    with open(f"{report_dir}/data-{str(uuid.uuid4())[:8]}.json", "w", encoding="utf-8") as f:
        json.dump(report.dict(), f, ensure_ascii=False, indent=4)


def _get_test_args(node_id: str, **kwargs):
    error_msg = (
        f"case_id is not set for {node_id}. Use testrail_case decorator, for example:"
        '@pytest.mark.testrail_case(case_id=12911, comment="some_comment"). Comment is optional'
    )

    try:
        case_id = kwargs["case_id"]
    except KeyError as exc:
        raise Exception(error_msg) from exc

    return case_id, kwargs.get("comment", "")


def get_case_id_and_comment_from_test(request: SubRequest) -> Tuple[int, Optional[str]]:
    """Get the case_id and comment for testrails integration.

    Returns:
        case_id: testrail test case ID
        comment: comment about the test case
    """
    for mark in request.node.own_markers:
        if mark.name == "testrail_test":
            testrail_params: dict = mark.kwargs
            break
    else:
        # NOTE: Indirect fixture usage with parametrize
        testrail_params: dict = request.param  # type: ignore[no-redef]

    return _get_test_args(
        request.node.nodeid,
        **testrail_params,
    )


def raise_if_status_code_differs(response: requests.Response, status_code: int) -> None:
    if not response.status_code == status_code:
        raise Exception(f"The response was not successful: {response.status_code} {response.text}")
