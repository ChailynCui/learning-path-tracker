from pydantic import BaseModel


class BackupImportRequest(BaseModel):
    data: dict[str, list[dict]]
