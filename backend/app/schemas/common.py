"""通用 schema 基类。"""
from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20