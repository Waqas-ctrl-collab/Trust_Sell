from app.models.category import CategoryDB

DEFAULT_CATEGORIES = [
    CategoryDB(
        slug="mobile",
        name="Mobile Phones",
        description="Smartphones, tablets, and accessories",
        icon="fa-mobile-alt",
        image_url="https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400&q=80",
        sort_order=1,
    ),
    CategoryDB(
        slug="cars",
        name="Cars & Vehicles",
        description="Cars, bikes, and commercial vehicles",
        icon="fa-car",
        image_url="https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=400&q=80",
        sort_order=2,
    ),
    CategoryDB(
        slug="property",
        name="Property",
        description="Houses, plots, and rentals",
        icon="fa-home",
        image_url="https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400&q=80",
        sort_order=3,
    ),
    CategoryDB(
        slug="electronics",
        name="Electronics",
        description="Laptops, TVs, and gadgets",
        icon="fa-laptop",
        image_url="https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&q=80",
        sort_order=4,
    ),
    CategoryDB(
        slug="fashion",
        name="Fashion",
        description="Clothing, shoes, and watches",
        icon="fa-tshirt",
        image_url="https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&q=80",
        sort_order=5,
    ),
    CategoryDB(
        slug="furniture",
        name="Furniture",
        description="Home and office furniture",
        icon="fa-couch",
        image_url="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80",
        sort_order=6,
    ),
    CategoryDB(
        slug="jobs",
        name="Jobs",
        description="Career opportunities across Pakistan",
        icon="fa-briefcase",
        image_url="https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=400&q=80",
        sort_order=7,
    ),
    CategoryDB(
        slug="services",
        name="Services",
        description="Professional and home services",
        icon="fa-tools",
        image_url="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&q=80",
        sort_order=8,
    ),
]


async def seed_categories_if_empty(db):
    collection = db["categories"]
    count = await collection.count_documents({})
    if count > 0:
        return
    for cat in DEFAULT_CATEGORIES:
        await collection.insert_one(cat.to_dict())
