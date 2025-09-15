from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Extra
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi import status

app = FastAPI()
# Database setup
# ----------------------------
# example_client = os.getenv("MONGO_URI_ARMAHAJAN")
client = MongoClient("mongodb+srv://rohitbobade1009_db_user:sTDpduYPkGUuoNZU@johndoe.uyatyav.mongodb.net/")  # Change if using Atlas
db = client["JohnDoe_DB"]          # Database ka naam
collection = db["JohnDoe_Col"]     # Collection ka naam



# Global handler for validation errors (422 -> 400)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Bad Request", "Error": exc.errors()},
    )



class Item(BaseModel):
    # Define your fields here, for example:
    first_name: str
    last_name: Optional[str] = None  # Optional field ke liye Optional use karo
    address: Optional[str] = None    # 'ddress' typo fix kiya


# Schema (sirf allowed fields)
class User(BaseModel, extra=Extra.forbid):
    name: str
    lname: str
    address: str

# Schema (sirf allowed fields)
class User(BaseModel, extra=Extra.forbid):
    name: str
    lname: str
    address: str

@app.post("/users")
def create_user(user: User):
    try:
        # Insert user data
        result = collection.insert_one(user.dict())
        return {
            "id": str(result.inserted_id),
            "message": "User created successfully",
            "data": user.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




# @app.post("/items/")
# def create_item(item: Item):
#     item_dict = item.dict()
#     result = collection.insert_one(item_dict)
    
#     # ObjectId ko string mein convert karo
#     item_dict["_id"] = str(result.inserted_id)

#     # Return response without ObjectId issues
#     return {
#         "id": str(result.inserted_id),
#         "message": "Item created successfully",
#         "data": item_dict
#     }

@app.get("/items/{inserted_id}")
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