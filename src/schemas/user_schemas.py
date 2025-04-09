from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., description="The unique username of the user.")



class UserCreate(UserBase):
    password: str = Field(..., min_length=3, description="The password for the user (at least 6 characters long).")


class UserRead(UserBase):
    id: int = Field(..., description="The unique identifier of the user.")
    created_at: datetime = Field(..., description="The timestamp when the user was created.")
    
