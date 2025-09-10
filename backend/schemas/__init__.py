import re

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class SupplierCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_person: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    city: str | None = Field(None, max_length=50)
    postal_code: str | None = Field(None, max_length=10)
    specialization: str | None = None
    website: HttpUrl | None = Field(None, max_length=200)
    notes: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            # Basic phone validation: at least contains some digits and valid characters
            phone_pattern = r"^[\d\s\-\+\(\)\.]+$"
            if not re.match(phone_pattern, v) or not any(char.isdigit() for char in v):
                raise ValueError("Phone number must contain digits and valid characters only")
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v):
        # Convert HttpUrl to string for database compatibility
        if v is not None:
            return str(v)
        return v


class SupplierUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    contact_person: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    city: str | None = Field(None, max_length=50)
    postal_code: str | None = Field(None, max_length=10)
    specialization: str | None = None
    website: HttpUrl | None = Field(None, max_length=200)
    notes: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            # Basic phone validation: at least contains some digits and valid characters
            phone_pattern = r"^[\d\s\-\+\(\)\.]+$"
            if not re.match(phone_pattern, v) or not any(char.isdigit() for char in v):
                raise ValueError("Phone number must contain digits and valid characters only")
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v):
        # Convert HttpUrl to string for database compatibility
        if v is not None:
            return str(v)
        return v


class PlantCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    common_name: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=50)
    height_min: float | None = Field(None, ge=0)
    height_max: float | None = Field(None, ge=0)
    width_min: float | None = Field(None, ge=0)
    width_max: float | None = Field(None, ge=0)
    sun_requirements: str | None = Field(None, max_length=50)
    soil_type: str | None = Field(None, max_length=100)
    water_needs: str | None = Field(None, max_length=50)
    hardiness_zone: str | None = Field(None, max_length=20)
    bloom_time: str | None = Field(None, max_length=100)
    bloom_color: str | None = Field(None, max_length=100)
    foliage_color: str | None = Field(None, max_length=100)
    native: bool | None = False
    supplier_id: int | None = Field(None, gt=0)
    price: float | None = Field(None, ge=0)
    availability: str | None = None
    planting_season: str | None = None
    maintenance: str | None = None
    notes: str | None = None


class PlantUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    common_name: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=50)
    height_min: float | None = Field(None, ge=0)
    height_max: float | None = Field(None, ge=0)
    width_min: float | None = Field(None, ge=0)
    width_max: float | None = Field(None, ge=0)
    sun_requirements: str | None = Field(None, max_length=50)
    soil_type: str | None = Field(None, max_length=100)
    water_needs: str | None = Field(None, max_length=50)
    hardiness_zone: str | None = Field(None, max_length=20)
    bloom_time: str | None = Field(None, max_length=100)
    bloom_color: str | None = Field(None, max_length=100)
    foliage_color: str | None = Field(None, max_length=100)
    native: bool | None = None
    supplier_id: int | None = Field(None, gt=0)
    price: float | None = Field(None, ge=0)
    availability: str | None = None
    planting_season: str | None = None
    maintenance: str | None = None
    notes: str | None = None


class ProductCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category: str | None = Field(None, max_length=50)
    price: float | None = Field(None, ge=0)
    unit: str | None = Field(None, max_length=20)
    supplier_id: int | None = Field(None, gt=0)
    stock_quantity: int | None = Field(None, ge=0)
    sku: str | None = Field(None, max_length=50)
    weight: float | None = Field(None, ge=0)
    dimensions: str | None = None
    notes: str | None = None


class ProductUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = Field(None, max_length=50)
    price: float | None = Field(None, ge=0)
    unit: str | None = Field(None, max_length=20)
    supplier_id: int | None = Field(None, gt=0)
    stock_quantity: int | None = Field(None, ge=0)
    sku: str | None = Field(None, max_length=50)
    weight: float | None = Field(None, ge=0)
    dimensions: str | None = None
    notes: str | None = None


class ClientCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_person: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    city: str | None = Field(None, max_length=50)
    postal_code: str | None = Field(None, max_length=10)
    client_type: str | None = Field(None, max_length=50)
    budget_range: str | None = None
    notes: str | None = None


class ClientUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    contact_person: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    city: str | None = Field(None, max_length=50)
    postal_code: str | None = Field(None, max_length=10)
    client_type: str | None = Field(None, max_length=50)
    budget_range: str | None = None
    notes: str | None = None


class ProjectCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    client_id: int = Field(..., gt=0)
    status: str | None = Field("Planning", max_length=50)
    start_date: str | None = None  # ISO date string
    end_date: str | None = None  # ISO date string
    budget: float | None = Field(None, ge=0)
    location: str | None = None
    project_type: str | None = Field(None, max_length=50)
    area_size: float | None = Field(None, ge=0)
    notes: str | None = None
    project_manager: str | None = Field("Hans Kmiel", max_length=100)


class ProjectUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    client_id: int | None = Field(None, gt=0)
    status: str | None = Field(None, max_length=50)
    start_date: str | None = None  # ISO date string
    end_date: str | None = None  # ISO date string
    budget: float | None = Field(None, ge=0)
    location: str | None = None
    project_type: str | None = Field(None, max_length=50)
    area_size: float | None = Field(None, ge=0)
    notes: str | None = None
    project_manager: str | None = Field(None, max_length=100)


class ProjectPlantCreateSchema(BaseModel):
    plant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_cost: float | None = Field(None, ge=0)
    notes: str | None = None


class ProjectPlantUpdateSchema(BaseModel):
    quantity: int | None = Field(None, gt=0)
    unit_cost: float | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=50)
    notes: str | None = None
