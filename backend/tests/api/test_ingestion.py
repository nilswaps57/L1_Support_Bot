from uuid import uuid4

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dependencies import PortDependencies


class Jobs:
    def __init__(self) -> None:
        job = IngestionJob.new(uuid4()).transition_to(IngestionStatus.PARSING)
        self.job = job

    async def get(self, job_id):
        return self.job if job_id == self.job.id else None


def test_job_status_exposes_progress_without_internal_failure_details() -> None:
    jobs = Jobs()
    app = create_app(Settings(), PortDependencies(ingestion_job_repository=jobs))

    response = TestClient(app).get(f"/api/v1/ingestion/jobs/{jobs.job.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "PARSING"
    assert "traceback" not in str(payload).lower()
    assert "/home/" not in str(payload)
