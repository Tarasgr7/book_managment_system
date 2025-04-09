from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token: str = Field(..., description="The JWT access token used for authentication.")
    token_type: str = Field(..., description="The type of the token, typically 'bearer'.")



class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="The email of the user, if available, embedded in the token.")

