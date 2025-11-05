from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class AppStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)  # In a real app, this would be hashed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AppUser(Base):
    __tablename__ = "app_users"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SchemaObject(Base):
    __tablename__ = "objects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    fields = Column(JSON, nullable=False)  # Store fields as JSON
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True)  # Reference to app
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SchemaRecord(Base):
    __tablename__ = "records"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    data = Column(JSON, nullable=False)  # Store record data as JSON
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SchemaWorkflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    steps = Column(JSON, nullable=False)  # Store steps as JSON
    layout = Column(JSON, nullable=True)  # Store layout as JSON
    app_id = Column(Integer, nullable=True, index=True)  # Reference to app
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SchemaApp(Base):
    __tablename__ = "apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(AppStatus), default=AppStatus.DRAFT, nullable=False)
    app_metadata = Column(JSON, nullable=True)  # Store additional app metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Metadata(Base):
    __tablename__ = "metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, index=True, unique=True)
    value = Column(JSON, nullable=False)  # Store configuration as JSON
    description = Column(Text, nullable=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True)  # Optional app-specific metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 