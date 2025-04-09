from pydantic import BaseModel, Field

class AuthorBase(BaseModel):
    name: str = Field(..., description="The name of the author.")

class AuthorCreate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    id: int = Field(..., description="The unique identifier of the author.")
