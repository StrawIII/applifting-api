from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, UUID, VARCHAR
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ProductORM(Base):
    __tablename__ = "product"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(50), unique=True)
    description: Mapped[str] = mapped_column(TEXT)

    offers: Mapped[list[OfferORM]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class OfferORM(Base):
    __tablename__ = "offer"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    price: Mapped[int] = mapped_column(INTEGER)
    items_in_stock: Mapped[int] = mapped_column(INTEGER)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"))

    product: Mapped[ProductORM] = relationship(back_populates="offers")
