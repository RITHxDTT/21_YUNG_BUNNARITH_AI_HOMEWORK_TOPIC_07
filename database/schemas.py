from enum import Enum

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class SearchProductsInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=100,
        description="Product name or category to search for",
    )


class CheckStockInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="ID of the product to check",
    )


class DeleteProductInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="ID of the product to delete",
    )