"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
The collection name is the lowercase of the class name.

This project stores real products, carts, and orders in MongoDB.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Product(BaseModel):
    """
    Products collection schema
    Collection: "product"
    """
    id: int = Field(..., description="Stable numeric id used by frontend routes")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Marketing description")
    category: str = Field(..., description="Category such as Face Care, Hair Care, Body Care")
    price: float = Field(..., ge=0, description="Unit price")
    image: str = Field(..., description="Image URL")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredient names")
    rating: float = Field(0.0, ge=0, le=5, description="Average rating 0-5")
    reviews: int = Field(0, ge=0, description="Number of reviews")
    stock: int = Field(0, ge=0, description="Available stock units")
    popularity: int = Field(0, ge=0, description="Popularity score for sorting")


class CartItem(BaseModel):
    """
    Cart items collection schema
    Collection: "cart"
    """
    cart_id: str = Field(..., description="Client-generated cart id")
    product_id: int = Field(..., ge=1)
    qty: int = Field(..., ge=1)


class Order(BaseModel):
    """
    Orders collection schema
    Collection: "order"
    """
    cart_id: str
    items: List[CartItem]
    total: float
    email: Optional[str] = None
    status: str = Field("created")


class User(BaseModel):
    """
    Users collection schema (placeholder for future auth)
    Collection: "user"
    """
    name: str
    email: str
    is_active: bool = True

