import os
import uuid
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document
from schemas import Product as ProductSchema, CartItem as CartItemSchema, Order as OrderSchema

app = FastAPI(title="Ayurvedic Cosmetics API", version="0.3.1")

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


# Seed products to DB one-time if collection empty
async def ensure_seed_data():
    if db is None:
        return
    existing = list(db["product"].find({}).limit(1))
    if existing:
        return
    seed_products: List[dict] = [
        {
            "id": 1,
            "name": "Sandalwood Glow Serum",
            "description": "A lightweight serum infused with pure sandalwood and saffron to brighten and calm the skin.",
            "category": "Face Care",
            "price": 24.99,
            "image": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?q=80&w=1200&auto=format&fit=crop",
            "ingredients": ["Sandalwood", "Saffron", "Aloe Vera"],
            "rating": 4.7,
            "reviews": 213,
            "stock": 42,
            "popularity": 940,
        },
        {
            "id": 2,
            "name": "Turmeric Repair Cream",
            "description": "Rich moisturizer with turmeric and ashwagandha for overnight repair and glow.",
            "category": "Face Care",
            "price": 19.5,
            "image": "https://images.unsplash.com/photo-1604881991720-f91add269bed?q=80&w=1200&auto=format&fit=crop",
            "ingredients": ["Turmeric", "Ashwagandha", "Ghee"],
            "rating": 4.6,
            "reviews": 156,
            "stock": 30,
            "popularity": 780,
        },
        {
            "id": 3,
            "name": "Neem & Tulsi Cleanser",
            "description": "Purifying gel cleanser with neem and tulsi to balance oil and clarify pores.",
            "category": "Face Care",
            "price": 12.0,
            "image": "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa0?q=80&w=1200&auto=format&fit=crop",
            "ingredients": ["Neem", "Tulsi", "Basil"],
            "rating": 4.4,
            "reviews": 98,
            "stock": 75,
            "popularity": 620,
        },
        {
            "id": 4,
            "name": "Amla Shine Hair Oil",
            "description": "Nourishing hair oil with amla and bhringraj for strong, glossy hair.",
            "category": "Hair Care",
            "price": 15.99,
            "image": "https://images.unsplash.com/photo-1608245449230-c0aeee29fc61?q=80&w=1200&auto=format&fit=crop",
            "ingredients": ["Amla", "Bhringraj", "Coconut Oil"],
            "rating": 4.5,
            "reviews": 321,
            "stock": 120,
            "popularity": 1100,
        },
        {
            "id": 5,
            "name": "Rose & Vetiver Body Butter",
            "description": "Deeply hydrating body butter with shea, rose, and vetiver for satin-soft skin.",
            "category": "Body Care",
            "price": 17.25,
            "image": "https://images.unsplash.com/photo-1619451334792-2506e2a5c1e5?q=80&w=1200&auto=format&fit=crop",
            "ingredients": ["Rose", "Vetiver", "Shea Butter"],
            "rating": 4.8,
            "reviews": 89,
            "stock": 28,
            "popularity": 540,
        },
        {
            "id": 6,
            "name": "Sandal-Turmeric Ubtan",
            "description": "Traditional Ayurvedic ubtan blend for exfoliation and glow.",
            "category": "Body Care",
            "price": 9.99,
            "image": "https://images.unsplash.com/photo-1516826957135-700dedea698c?q=80&w=1200&auto=format&fit=crop",
            "ingredients": ["Sandalwood", "Turmeric", "Gram Flour"],
            "rating": 4.3,
            "reviews": 45,
            "stock": 64,
            "popularity": 430,
        },
    ]
    for doc in seed_products:
        try:
            create_document("product", doc)
        except Exception:
            pass


@app.on_event("startup")
async def on_startup():
    await ensure_seed_data()


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
    if db is not None:
        query = {}
        if category:
            query["category"] = category
        if ingredient:
            query["ingredients"] = {"$regex": ingredient, "$options": "i"}
        if q:
            query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
            ]
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            query["price"] = price_filter

        sort_spec = None
        if sort == "price_asc":
            sort_spec = [("price", 1)]
        elif sort == "price_desc":
            sort_spec = [("price", -1)]
        elif sort == "name_asc":
            sort_spec = [("name", 1)]
        elif sort == "name_desc":
            sort_spec = [("name", -1)]
        elif sort == "popularity":
            sort_spec = [("popularity", -1)]
        elif sort == "rating":
            sort_spec = [("rating", -1)]

        cursor = db["product"].find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        results = list(cursor)
        mapped = [
            Product(
                id=doc.get("id"),
                name=doc.get("name"),
                description=doc.get("description", ""),
                category=doc.get("category", ""),
                price=float(doc.get("price", 0)),
                image=doc.get("image", ""),
                ingredients=list(doc.get("ingredients", [])),
                rating=float(doc.get("rating", 0)),
                reviews=int(doc.get("reviews", 0)),
                stock=int(doc.get("stock", 0)),
                popularity=int(doc.get("popularity", 0)),
            )
            for doc in results
        ]
        return mapped

    # fallback mock
    fallback: List[Product] = [
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
    return fallback


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    if db is not None:
        doc = db["product"].find_one({"id": product_id})
        if doc:
            return Product(
                id=doc.get("id"),
                name=doc.get("name"),
                description=doc.get("description", ""),
                category=doc.get("category", ""),
                price=float(doc.get("price", 0)),
                image=doc.get("image", ""),
                ingredients=list(doc.get("ingredients", [])),
                rating=float(doc.get("rating", 0)),
                reviews=int(doc.get("reviews", 0)),
                stock=int(doc.get("stock", 0)),
                popularity=int(doc.get("popularity", 0)),
            )
    # Fallback search
    for p in list_products():
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/api/cart/start")
def start_cart():
    cart_id = str(uuid.uuid4())
    return {"cart_id": cart_id}


class AddToCartRequest(BaseModel):
    cart_id: str
    product_id: int
    qty: int = 1


@app.post("/api/cart/add")
def add_to_cart(body: AddToCartRequest):
    if db is None:
        # For mock mode, do nothing but echo back
        return {"ok": True, "cart_id": body.cart_id}
    # Validate product exists
    prod = db["product"].find_one({"id": body.product_id})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    create_document("cart", {
        "cart_id": body.cart_id,
        "product_id": body.product_id,
        "qty": int(max(1, body.qty)),
    })
    return {"ok": True, "cart_id": body.cart_id}


@app.get("/api/cart/{cart_id}")
def get_cart(cart_id: str):
    items = []
    if db is not None:
        items = list(db["cart"].find({"cart_id": cart_id}))
    total = 0.0
    detailed = []
    for it in items:
        prod = db["product"].find_one({"id": it.get("product_id")}) if db is not None else None
        if not prod:
            continue
        qty = int(it.get("qty", 1))
        price = float(prod.get("price", 0))
        total += price * qty
        detailed.append({
            "product_id": prod.get("id"),
            "name": prod.get("name"),
            "price": price,
            "qty": qty,
            "image": prod.get("image"),
        })
    return {"items": detailed, "total": round(total, 2)}


class CheckoutRequest(BaseModel):
    cart_id: str
    email: Optional[str] = None


@app.post("/api/checkout")
def checkout(body: CheckoutRequest):
    if db is None:
        return {"ok": True, "status": "mock", "order_id": str(uuid.uuid4())}
    items = list(db["cart"].find({"cart_id": body.cart_id}))
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total = 0.0
    for it in items:
        prod = db["product"].find_one({"id": it.get("product_id")})
        if not prod:
            continue
        total += float(prod.get("price", 0)) * int(it.get("qty", 1))
    order_doc = {
        "cart_id": body.cart_id,
        "items": items,
        "total": round(total, 2),
        "email": body.email,
        "status": "created",
    }
    order_id = create_document("order", order_doc)
    # Clear cart after checkout
    db["cart"].delete_many({"cart_id": body.cart_id})
    return {"ok": True, "order_id": order_id}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "✅ Using MongoDB" if db is not None else "❌ Not Used (mock mode)",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Connected" if db is not None else "Mock",
        "collections": [],
    }

    if db is not None:
        try:
            response["collections"] = sorted(db.list_collection_names())
        except Exception:
            response["collections"] = []
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
