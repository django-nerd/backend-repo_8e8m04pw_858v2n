import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Ayurvedic Cosmetics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: float
    image: str
    ingredients: List[str]
    rating: float
    reviews: int
    stock: int
    popularity: int


# Mock dataset (placeholder for real database)
PRODUCTS: List[Product] = [
    Product(
        id=1,
        name="Sandalwood Glow Serum",
        description="A lightweight serum infused with pure sandalwood and saffron to brighten and calm the skin.",
        category="Face Care",
        price=24.99,
        image="https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?q=80&w=1200&auto=format&fit=crop",
        ingredients=["Sandalwood", "Saffron", "Aloe Vera"],
        rating=4.7,
        reviews=213,
        stock=42,
        popularity=940,
    ),
    Product(
        id=2,
        name="Turmeric Repair Cream",
        description="Rich moisturizer with turmeric and ashwagandha for overnight repair and glow.",
        category="Face Care",
        price=19.5,
        image="https://images.unsplash.com/photo-1604881991720-f91add269bed?q=80&w=1200&auto=format&fit=crop",
        ingredients=["Turmeric", "Ashwagandha", "Ghee"],
        rating=4.6,
        reviews=156,
        stock=30,
        popularity=780,
    ),
    Product(
        id=3,
        name="Neem & Tulsi Cleanser",
        description="Purifying gel cleanser with neem and tulsi to balance oil and clarify pores.",
        category="Face Care",
        price=12.0,
        image="https://images.unsplash.com/photo-1612815154858-60aa4c59eaa0?q=80&w=1200&auto=format&fit=crop",
        ingredients=["Neem", "Tulsi", "Basil"],
        rating=4.4,
        reviews=98,
        stock=75,
        popularity=620,
    ),
    Product(
        id=4,
        name="Amla Shine Hair Oil",
        description="Nourishing hair oil with amla and bhringraj for strong, glossy hair.",
        category="Hair Care",
        price=15.99,
        image="https://images.unsplash.com/photo-1608245449230-c0aeee29fc61?q=80&w=1200&auto=format&fit=crop",
        ingredients=["Amla", "Bhringraj", "Coconut Oil"],
        rating=4.5,
        reviews=321,
        stock=120,
        popularity=1100,
    ),
    Product(
        id=5,
        name="Rose & Vetiver Body Butter",
        description="Deeply hydrating body butter with shea, rose, and vetiver for satin-soft skin.",
        category="Body Care",
        price=17.25,
        image="https://images.unsplash.com/photo-1619451334792-2506e2a5c1e5?q=80&w=1200&auto=format&fit=crop",
        ingredients=["Rose", "Vetiver", "Shea Butter"],
        rating=4.8,
        reviews=89,
        stock=28,
        popularity=540,
    ),
    Product(
        id=6,
        name="Sandal-Turmeric Ubtan",
        description="Traditional Ayurvedic ubtan blend for exfoliation and glow.",
        category="Body Care",
        price=9.99,
        image="https://images.unsplash.com/photo-1516826957135-700dedea698c?q=80&w=1200&auto=format&fit=crop",
        ingredients=["Sandalwood", "Turmeric", "Gram Flour"],
        rating=4.3,
        reviews=45,
        stock=64,
        popularity=430,
    ),
]


@app.get("/")
def read_root():
    return {"message": "Ayurvedic Cosmetics API is running"}


@app.get("/api/products", response_model=List[Product])
def list_products(
    category: Optional[str] = Query(None),
    ingredient: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search query"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: Optional[str] = Query(None, description="price_asc|price_desc|name_asc|name_desc|popularity|rating"),
):
    results = PRODUCTS

    if category:
        results = [p for p in results if p.category.lower() == category.lower()]
    if ingredient:
        results = [p for p in results if any(ingredient.lower() in ing.lower() for ing in p.ingredients)]
    if q:
        results = [
            p
            for p in results
            if q.lower() in p.name.lower() or q.lower() in p.description.lower()
        ]
    if min_price is not None:
        results = [p for p in results if p.price >= min_price]
    if max_price is not None:
        results = [p for p in results if p.price <= max_price]

    if sort:
        if sort == "price_asc":
            results = sorted(results, key=lambda x: x.price)
        elif sort == "price_desc":
            results = sorted(results, key=lambda x: x.price, reverse=True)
        elif sort == "name_asc":
            results = sorted(results, key=lambda x: x.name)
        elif sort == "name_desc":
            results = sorted(results, key=lambda x: x.name, reverse=True)
        elif sort == "popularity":
            results = sorted(results, key=lambda x: x.popularity, reverse=True)
        elif sort == "rating":
            results = sorted(results, key=lambda x: x.rating, reverse=True)

    return results


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for p in PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Used (mock mode)",
        "database_url": None,
        "database_name": None,
        "connection_status": "Mock",
        "collections": [],
    }

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
