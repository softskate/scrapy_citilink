from pydantic import BaseModel, ConfigDict
from typing import Optional

    
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    groupId: Optional[str] = None
    name: str
    productUrl: str
    price: float
    
class ProductDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    groupId: Optional[str] = None
    imageUrls: list
    name: str
    price: int
    brandName: Optional[str] = None
    description: Optional[str] = None
    details: Optional[dict] = None
    productUrl: str
    
class ParsingItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    link: str

