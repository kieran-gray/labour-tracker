from pydantic import BaseModel

from app.application.dtos.labour import LabourDTO
from app.application.dtos.labour_summary import LabourSummaryDTO


class LabourResponse(BaseModel):
    labour: LabourDTO


class LabourSummaryResponse(BaseModel):
    labour: LabourSummaryDTO
