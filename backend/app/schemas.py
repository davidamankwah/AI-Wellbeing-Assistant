from pydantic import BaseModel, EmailStr, ConfigDict,Field
from enum import Enum


#schema used when creating/registering a new user
class UserCreate(BaseModel):
    username:str 
    email:EmailStr
    password: str

#schema used when logging in
class UserLogin(BaseModel):
    username: str
    password: str

# schema used when returning user information
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True) # allows pydantic to read data from a SQLAlchemy object

# schema used when returning an access token
class Token(BaseModel):
    access_token: str
    token_type: str

# Student request for chat sent
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

#The response is given by FastAPI.
class ChatResponse(BaseModel):
    response: str
    status: str

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class MessageClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wellbeing_scope: bool
    safeguarding_risk: RiskLevel
    prompt_injection: bool
    clinical_request: bool
    risk_reason: str = Field(min_length=1, max_length=500)
