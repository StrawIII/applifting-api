from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer

from api.schemas.offer import Offer


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductFromORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime


class ProductCatalogue(ProductFromORM):
    id: UUID
    name: str
    description: str
    offers: list[Offer]

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductCreateIn(ProductBase):
    id: UUID
    name: str
    description: str

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductCreateOut(ProductFromORM):
    id: UUID
    name: str
    description: str

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductRead(ProductFromORM):
    id: UUID
    name: str
    description: str

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductUpdateIn(ProductBase):
    name: str
    description: str


class ProductUpdateOut(ProductFromORM):
    name: str
    description: str


class ProductDelete(ProductBase):
    id: UUID

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
