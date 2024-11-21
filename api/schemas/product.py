from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer

from api.schemas.offer import Offer


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductCatalogue(ProductBase):
    id: UUID
    name: str
    description: str
    offers: list[Offer]

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductCreate(ProductBase):
    id: UUID
    name: str
    description: str

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductRead(ProductBase):
    id: UUID
    name: str
    description: str

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class ProductUpdate(ProductBase):
    name: str
    description: str


class ProductDelete(ProductBase):
    id: UUID

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
