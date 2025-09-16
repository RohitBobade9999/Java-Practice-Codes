from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel, Extra, constr,Field
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi import status



app = FastAPI()

client = MongoClient("mongodb+srv://rohitbobade1009_db_user:sTDpduYPkGUuoNZU@johndoe.uyatyav.mongodb.net/")  # Change if using Atlas
db = client["JohnDoe_DB"]          # Database ka naam
collection = db["Recipe"]     # Collection ka naam


# Global handler for validation errors (422 -> 400)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Bad Request", "Error": exc.errors()},
    )


    # Define your fields here, for example:
    # title: str
class Recipe(BaseModel, extra=Extra.forbid):
    title: constr(regex=r'^[A-Za-z ]{3,50}$')
    ingredients: List[constr(regex=r'^[A-Za-z ]{2,20}$')] = Field(..., min_items=1)
    steps: List[str]
    cook_time: int

 
@app.post("/recipes")
def add_recipe(recipe: Recipe):
    # result = collection.insert_one(recipe.dict())
    # return {"id": str(result.inserted_id)}
    existing = collection.find_one({
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "steps": recipe.steps,
        "cook_time": recipe.cook_time
    })
    if existing:
        raise HTTPException(status_code=400, detail="Duplicate recipe already exists")

    result = collection.insert_one(recipe.dict())
    return {"id": str(result.inserted_id)}
    

def serialize_recipe(recipe):
    recipe["_id"] = str(recipe["_id"])  # convert ObjectId to string
    return recipe


# Get all recipe

@app.get("/recipes/all")
def fetch_allRecipe():
 all_recipes = collection.find()  # fetches all documents
 return [serialize_recipe(r) for r in all_recipes]


@app.get("/recipes/{inserted_id}")
def get_item(inserted_id: str):
    # Convert string ID to ObjectId
    try:
        obj_id = ObjectId(inserted_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Find item in MongoDB
    item = collection.find_one({"_id": obj_id})

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Convert ObjectId to string before returning
    item["_id"] = str(item["_id"])

    return {
        "id": inserted_id,
        "message": "Item fetched successfully",
        "data": item
    }


@app.get("/recipes")
def fetch_recipes(ingredient: str = Query(None)):
    query = {}
    if ingredient:
        query["ingredients"] = {"$elemMatch": {"$regex": f"^{ingredient}$", "$options": "i"}}
    
    print("Mongo Query:", query)   #  debug line
    
    all_recipes = collection.find(query)
    return [serialize_recipe(r) for r in all_recipes]


# ================= Hello Rohit ============
    