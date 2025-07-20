"""
This module shows different ways to programmatically create a sanitized
'public' version of any private Pydantic data model (e.g., to avoid
leaking sensitive fields to the client in an API response.

The demonstrated methods include Python implementations of Typescript's
'omit' and 'pick'
"""

from pydantic import BaseModel, Field, create_model
from typing import Type, Set, Dict, Any

# What we're trying to avoid: using `model_dump` with `exclude` for serialization (unsafe!)
def serialize_without_fields(model: BaseModel, exclude_fields: Set[str]) -> Dict[str, Any]:
    """Serialize model excluding specified fields"""
    return model.model_dump(exclude=exclude_fields)


def omit_fields(model_class: Type[BaseModel], exclude_fields: Set[str]) -> Type[BaseModel]:
    """
    Create a new Pydantic model by omitting specified fields from an existing model.
    Similar to TypeScript's Omit<Type, Keys> utility type.
    """
    original_fields = model_class.model_fields
    
    # Validate that all exclude_fields exist in the original model
    invalid_fields = exclude_fields - set(original_fields.keys())
    if invalid_fields:
        raise ValueError(f"Fields {invalid_fields} do not exist in {model_class.__name__}")
    
    new_fields = {}

    for field_name, field_info in original_fields.items():
        if field_name not in exclude_fields:
            new_fields[field_name] = (field_info.annotation, field_info)

    new_model_name = f"{model_class.__name__}Without{''.join(sorted(exclude_fields))}"
    return create_model(new_model_name, **new_fields)


def pick_fields(model_class: Type[BaseModel], include_fields: Set[str]) -> Type[BaseModel]:
    """
    Create a new Pydantic model by picking only specified fields from an existing model.
    Similar to TypeScript's Pick<Type, Keys> utility type.
    """
    original_fields = model_class.model_fields
    
    # Validate that all include_fields exist in the original model
    invalid_fields = include_fields - set(original_fields.keys())
    if invalid_fields:
        raise ValueError(f"Fields {invalid_fields} do not exist in {model_class.__name__}")
    
    new_fields = {}
    
    for field_name, field_info in original_fields.items():
        if field_name in include_fields:
            new_fields[field_name] = (field_info.annotation, field_info)
    
    new_model_name = f"{model_class.__name__}With{''.join(sorted(include_fields))}"
    return create_model(new_model_name, **new_fields)


class User(BaseModel):
    """Private user model with sensitive fields"""
    id: int = Field(description="User ID")
    username: str = Field(description="Public username")
    email: str = Field(description="Email address")
    password_hash: str = Field(description="Hashed password")
    api_key: str = Field(description="API access key")
    ssn: str = Field(description="Social Security Number")
    created_at: str = Field(description="Account creation timestamp")


# Method 1: Using custom `omit_fields`` function
PublicUser = omit_fields(User, {'password_hash', 'api_key', 'ssn'})

# Method 2: Using custom `pick_fields`` function
MinimalUser = pick_fields(User, {'id', 'username'})


if __name__ == "__main__":
    # Create original user with sensitive data
    original_user = User(
        id=123,
        username="john_doe",
        email="john@example.com",
        password_hash="$2b$12$abcd1234...",
        api_key="sk-1234567890abcdef",
        ssn="123-45-6789",
        created_at="2024-01-15T10:30:00Z"
    )
    print("Original User (contains sensitive data):")
    print(original_user.model_dump())
    print()
    
    # Unsafe method: Runtime exclusion with typo
    serialized = serialize_without_fields(
        original_user, {'password_hash', 'api_key', 'ss'}  # Typo: 'ss' instead of 'ssn'
    )
    print("Serialization with 'exclude' (typo in field name):")
    print(serialized)
    print("🚨 SECURITY RISK: SSN leaked due to typo!")
    print()

    # Method 1: Using omit_fields (safe)
    public_user = PublicUser(
        id=123,
        username="john_doe",
        email="john@example.com",
        created_at="2024-01-15T10:30:00Z"
    )
    print("Public User (sensitive fields omitted at compile time):")
    print(public_user.model_dump())
    print()

    # Method 2: Using pick_fields (safe)
    minimal_user = MinimalUser(
        id=123,
        username="john_doe"
    )
    print("Minimal User (only safe fields picked at compile time):")
    print(minimal_user.model_dump())
    print()