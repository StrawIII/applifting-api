from uuid import UUID

from pydantic import BaseModel, field_serializer


class Offer(BaseModel):
    id: UUID
    price: int
    items_in_stock: int

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
