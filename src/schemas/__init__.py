from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class SupplierCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    specialization: Optional[str] = None
    website: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class SupplierUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    specialization: Optional[str] = None
    website: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class PlantCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    height_min: Optional[float] = Field(None, ge=0)
    height_max: Optional[float] = Field(None, ge=0)
    width_min: Optional[float] = Field(None, ge=0)
    width_max: Optional[float] = Field(None, ge=0)
    sun_requirements: Optional[str] = Field(None, max_length=50)
    soil_type: Optional[str] = Field(None, max_length=100)
    water_needs: Optional[str] = Field(None, max_length=50)
    hardiness_zone: Optional[str] = Field(None, max_length=20)
    bloom_time: Optional[str] = Field(None, max_length=100)
    bloom_color: Optional[str] = Field(None, max_length=100)
    foliage_color: Optional[str] = Field(None, max_length=100)
    native: Optional[bool] = False
    supplier_id: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0)
    availability: Optional[str] = None
    planting_season: Optional[str] = None
    maintenance: Optional[str] = None
    notes: Optional[str] = None


class PlantUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    height_min: Optional[float] = Field(None, ge=0)
    height_max: Optional[float] = Field(None, ge=0)
    width_min: Optional[float] = Field(None, ge=0)
    width_max: Optional[float] = Field(None, ge=0)
    sun_requirements: Optional[str] = Field(None, max_length=50)
    soil_type: Optional[str] = Field(None, max_length=100)
    water_needs: Optional[str] = Field(None, max_length=50)
    hardiness_zone: Optional[str] = Field(None, max_length=20)
    bloom_time: Optional[str] = Field(None, max_length=100)
    bloom_color: Optional[str] = Field(None, max_length=100)
    foliage_color: Optional[str] = Field(None, max_length=100)
    native: Optional[bool] = None
    supplier_id: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0)
    availability: Optional[str] = None
    planting_season: Optional[str] = None
    maintenance: Optional[str] = None
    notes: Optional[str] = None


class ProductCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    supplier_id: Optional[int] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=50)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = None
    notes: Optional[str] = None


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    supplier_id: Optional[int] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=50)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = None
    notes: Optional[str] = None


class ClientCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    client_type: Optional[str] = Field(None, max_length=50)
    budget_range: Optional[str] = None
    notes: Optional[str] = None


class ClientUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    client_type: Optional[str] = Field(None, max_length=50)
    budget_range: Optional[str] = None
    notes: Optional[str] = None


class ProjectCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    client_id: int = Field(..., gt=0)
    status: Optional[str] = Field("Planning", max_length=50)
    start_date: Optional[str] = None  # ISO date string
    end_date: Optional[str] = None  # ISO date string
    budget: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    project_type: Optional[str] = Field(None, max_length=50)
    area_size: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    project_manager: Optional[str] = Field("Hans Kmiel", max_length=100)


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    client_id: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, max_length=50)
    start_date: Optional[str] = None  # ISO date string
    end_date: Optional[str] = None  # ISO date string
    budget: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    project_type: Optional[str] = Field(None, max_length=50)
    area_size: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    project_manager: Optional[str] = Field(None, max_length=100)


class ProjectPlantCreateSchema(BaseModel):
    plant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class ProjectPlantUpdateSchema(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
