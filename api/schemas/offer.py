from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class Offer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    price: int
    items_in_stock: int

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
