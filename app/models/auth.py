from pydantic import BaseModel, EmailStr

class LoginData(BaseModel):
    email: str
    password: str

class SignupData(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str 