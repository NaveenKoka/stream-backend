#!/usr/bin/env python3
"""
Script to seed field types metadata into the database.
Run this after creating the metadata table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Metadata

def seed_field_types():
    """Seed field types metadata"""
    
    # Default field types configuration with new structure
    field_types_config = {
        "field_types": {
            "types": [
                {
                    "value": "string",
                    "label": "Text",
                    "description": "Single line text input",
                    "category": "basic",
                    "validation": {
                        "max_length": 255,
                        "required": False,
                        "pattern": None
                    },
                    "ui": {
                        "input_type": "text",
                        "placeholder": "Enter text..."
                    }
                },
                {
                    "value": "text",
                    "label": "Long Text",
                    "description": "Multi-line text input",
                    "category": "basic",
                    "validation": {
                        "max_length": 10000,
                        "required": False
                    },
                    "ui": {
                        "input_type": "textarea",
                        "rows": 4,
                        "placeholder": "Enter long text..."
                    }
                },
                {
                    "value": "number",
                    "label": "Number",
                    "description": "Numeric input with decimal support",
                    "category": "numeric",
                    "validation": {
                        "min": None,
                        "max": None,
                        "decimal_places": 2,
                        "required": False
                    },
                    "ui": {
                        "input_type": "number",
                        "step": 0.01,
                        "placeholder": "0.00"
                    }
                },
                {
                    "value": "integer",
                    "label": "Integer",
                    "description": "Whole number input",
                    "category": "numeric",
                    "validation": {
                        "min": None,
                        "max": None,
                        "required": False
                    },
                    "ui": {
                        "input_type": "number",
                        "step": 1,
                        "placeholder": "0"
                    }
                },
                {
                    "value": "boolean",
                    "label": "Boolean",
                    "description": "True/False checkbox",
                    "category": "basic",
                    "validation": {
                        "default": False,
                        "required": False
                    },
                    "ui": {
                        "input_type": "checkbox"
                    }
                },
                {
                    "value": "date",
                    "label": "Date",
                    "description": "Date picker",
                    "category": "datetime",
                    "validation": {
                        "format": "YYYY-MM-DD",
                        "min_date": None,
                        "max_date": None,
                        "required": False
                    },
                    "ui": {
                        "input_type": "date"
                    }
                },
                {
                    "value": "datetime",
                    "label": "Date & Time",
                    "description": "Date and time picker",
                    "category": "datetime",
                    "validation": {
                        "format": "YYYY-MM-DD HH:MM:SS",
                        "timezone": "UTC",
                        "required": False
                    },
                    "ui": {
                        "input_type": "datetime-local"
                    }
                },
                {
                    "value": "email",
                    "label": "Email",
                    "description": "Email address input",
                    "category": "contact",
                    "validation": {
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        "required": False
                    },
                    "ui": {
                        "input_type": "email",
                        "placeholder": "user@example.com"
                    }
                },
                {
                    "value": "phone",
                    "label": "Phone",
                    "description": "Phone number input",
                    "category": "contact",
                    "validation": {
                        "pattern": "^[+]?[0-9\\s\\-\\(\\)]{10,}$",
                        "required": False
                    },
                    "ui": {
                        "input_type": "tel",
                        "placeholder": "+1 (555) 123-4567"
                    }
                },
                {
                    "value": "url",
                    "label": "URL",
                    "description": "Website URL input",
                    "category": "basic",
                    "validation": {
                        "pattern": "^https?:\\/\\/.+",
                        "required": False
                    },
                    "ui": {
                        "input_type": "url",
                        "placeholder": "https://example.com"
                    }
                },
                {
                    "value": "currency",
                    "label": "Currency",
                    "description": "Money amount input",
                    "category": "numeric",
                    "validation": {
                        "currency_code": "USD",
                        "decimal_places": 2,
                        "min": 0,
                        "max": None,
                        "required": False
                    },
                    "ui": {
                        "input_type": "number",
                        "step": 0.01,
                        "prefix": "$",
                        "placeholder": "0.00"
                    }
                },
                {
                    "value": "percentage",
                    "label": "Percentage",
                    "description": "Percentage input (0-100)",
                    "category": "numeric",
                    "validation": {
                        "min": 0,
                        "max": 100,
                        "decimal_places": 2,
                        "required": False
                    },
                    "ui": {
                        "input_type": "number",
                        "step": 0.01,
                        "suffix": "%",
                        "placeholder": "0.00"
                    }
                },
                {
                    "value": "select",
                    "label": "Select",
                    "description": "Dropdown selection",
                    "category": "choice",
                    "validation": {
                        "options": [],
                        "multiple": False,
                        "required": False,
                        "allow_custom": False
                    },
                    "ui": {
                        "input_type": "select",
                        "placeholder": "Select an option..."
                    }
                },
                {
                    "value": "multiselect",
                    "label": "Multi-Select",
                    "description": "Multiple selection dropdown",
                    "category": "choice",
                    "validation": {
                        "options": [],
                        "multiple": True,
                        "required": False,
                        "allow_custom": False
                    },
                    "ui": {
                        "input_type": "select",
                        "multiple": True,
                        "placeholder": "Select options..."
                    }
                },
                {
                    "value": "reference",
                    "label": "Reference",
                    "description": "Foreign key relationship to another object",
                    "category": "relationship",
                    "validation": {
                        "referenced_object": None,
                        "referenced_field": "id",
                        "required": False,
                        "cascade_delete": False,
                        "on_update": "CASCADE"
                    },
                    "ui": {
                        "input_type": "select",
                        "placeholder": "Select related record...",
                        "searchable": True,
                        "display_field": "name"
                    }
                },
                {
                    "value": "file",
                    "label": "File Upload",
                    "description": "File upload input",
                    "category": "media",
                    "validation": {
                        "allowed_types": ["pdf", "doc", "docx", "txt", "csv"],
                        "max_size": "10MB",
                        "required": False,
                        "multiple": False
                    },
                    "ui": {
                        "input_type": "file",
                        "accept": ".pdf,.doc,.docx,.txt,.csv"
                    }
                },
                {
                    "value": "image",
                    "label": "Image Upload",
                    "description": "Image file upload",
                    "category": "media",
                    "validation": {
                        "allowed_types": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
                        "max_size": "5MB",
                        "required": False,
                        "multiple": False
                    },
                    "ui": {
                        "input_type": "file",
                        "accept": "image/*"
                    }
                }
            ],
            "categories": [
                {
                    "id": "basic",
                    "name": "Basic",
                    "description": "Basic input types"
                },
                {
                    "id": "numeric",
                    "name": "Numeric",
                    "description": "Number-related inputs"
                },
                {
                    "id": "datetime",
                    "name": "Date & Time",
                    "description": "Date and time inputs"
                },
                {
                    "id": "contact",
                    "name": "Contact",
                    "description": "Contact information inputs"
                },
                {
                    "id": "choice",
                    "name": "Choice",
                    "description": "Selection and choice inputs"
                },
                {
                    "id": "relationship",
                    "name": "Relationship",
                    "description": "Object relationships and references"
                },
                {
                    "id": "media",
                    "name": "Media",
                    "description": "File and image uploads"
                }
            ]
        }
    }
    
    db = SessionLocal()
    try:
        # Check if field_types metadata already exists
        existing = db.query(Metadata).filter(Metadata.key == "field_types").first()
        
        if existing:
            print("Field types metadata already exists. Updating...")
            existing.value = field_types_config
            existing.description = "Available field types for object creation"
        else:
            print("Creating field types metadata...")
            metadata = Metadata(
                key="field_types",
                value=field_types_config,
                description="Available field types for object creation"
            )
            db.add(metadata)
        
        db.commit()
        print("✅ Field types metadata seeded successfully!")
        
        # Also create app-specific field types example
        app_specific_types = {
            "field_types": {
                "types": [
                    {
                        "value": "priority",
                        "label": "Priority",
                        "description": "Task/Issue priority level",
                        "category": "choice",
                        "validation": {
                            "options": ["Low", "Medium", "High", "Critical"],
                            "default": "Medium",
                            "required": True
                        },
                        "ui": {
                            "input_type": "select",
                            "placeholder": "Select priority..."
                        }
                    },
                    {
                        "value": "status",
                        "label": "Status",
                        "description": "Workflow status",
                        "category": "choice",
                        "validation": {
                            "options": ["Draft", "In Progress", "Completed", "Cancelled"],
                            "default": "Draft",
                            "required": True
                        },
                        "ui": {
                            "input_type": "select",
                            "placeholder": "Select status..."
                        }
                    }
                ]
            }
        }
        
        # Create app-specific example (for app_id=1)
        existing_app = db.query(Metadata).filter(
            Metadata.key == "field_types",
            Metadata.app_id == 1
        ).first()
        
        if not existing_app:
            app_metadata = Metadata(
                key="field_types",
                value=app_specific_types,
                description="App-specific field types for Field Service App",
                app_id=1
            )
            db.add(app_metadata)
            db.commit()
            print("✅ App-specific field types example created for App ID 1!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding field types: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding field types metadata...")
    seed_field_types()
    print("Done!")