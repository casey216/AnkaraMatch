from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    access_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True