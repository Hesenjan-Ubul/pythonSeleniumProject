from collections import defaultdict
from typing import Optional

from pydantic import BaseModel, Field

from src.config import PipelineMetaConfig


class RunModel(BaseModel):
    name: str
    url: Optional[str] = Field(
        description="Link to the testrail. Is added in publish-to-testrail step and sent to Mattermost in publish-to-mattermost"
    )


class CustomStepResult(BaseModel):
    content: str
    expected: str
    status_id: int
    actual: Optional[str]
    tags: list[str]


class TestRailTestResultModel(BaseModel):
    status_id: int
    test_id: Optional[
        int
    ]  # The id which groups test results together, e.g. the id in this link: https://celus.testrail.io/index.php?/tests/view/855066
    elapsed: str
    comment: str
    custom_step_results: list[CustomStepResult]


class CaseModel(BaseModel):
    case_id: int
    title: str
    parameter_title: Optional[str] = Field(
        description=(
            "Title of the parameter for the case which is used for parametrization."
            "This information is sent to Mattermost to enrich the report"
        )
    )
    test_result: TestRailTestResultModel


class ReportModel(BaseModel):
    run: RunModel
    cases: list[CaseModel]


IndexedReport = defaultdict[int, list[CaseModel]]


class ReportSummary(BaseModel):
    pipeline: PipelineMetaConfig
    report_run: RunModel
    indexed_report: IndexedReport
    num_failed: int
    num_total: int
