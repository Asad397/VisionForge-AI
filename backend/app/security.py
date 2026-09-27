from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    credits: int
    is_admin: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class ModelSchema(BaseModel):
    id: int
    name: str
    provider: str
    type: str
    description: Optional[str] = None
    enabled: bool = True
    credit_cost: int = 10
    capabilities: List[str] = []
    max_duration: int = 10
    supported_resolutions: List[str] = []
    supported_ratios: List[str] = []
    settings_schema: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class GenerationCreate(BaseModel):
    generation_type: str
    model_id: int
    prompt: str
    negative_prompt: Optional[str] = None
    duration: int = 5
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = '16:9'
    reference_images: List[str] = []
    settings: Dict[str, Any] = {}


class GenerationResponse(BaseModel):
    id: int
    user_id: int
    model_id: int
    generation_type: str
    prompt: str
    status: str
    provider: str
    model_name: str
    resolution: Optional[str]
    duration: int
    progress: int
    error_message: Optional[str]
    output_url: Optional[str]

    class Config:
        from_attributes = True


class CreditTransactionResponse(BaseModel):
    id: int
    amount: int
    reason: str
    balance_after: int

    class Config:
        from_attributes = True


class CharacterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    visual_description: Optional[str] = None
    style: Optional[str] = None
    metadata: Dict[str, Any] = {}


class FileUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    object_key: str
    size: int

    class Config:
        from_attributes = True
