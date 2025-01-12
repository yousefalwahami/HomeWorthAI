# controllers/items.py
from fastapi import APIRouter

# Create a router instance
router = APIRouter()

# Define routes related to items
@router.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
  return {"item_id": item_id, "q": q}

@router.get("/items")
def get_items():
  return {"items": ["item1", "item2", "item3"]}
