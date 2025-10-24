# Issue 03: Enhanced Error Handling - Update 20250901

**Original Issue**: #256  
**Priority**: CRITICAL - Phase 1 Foundation  
**Estimated Effort**: 6-10 hours  
**Dependencies**: Issue 02 (Backend Architecture)  
**Copilot Automation**: Ready

## Current State Assessment

**Error Handling Analysis**:
- ✅ **Basic Framework**: `src/utils/error_handlers.py` exists
- ⚠️ **Domain-Specific Exceptions**: Limited landscape architecture context
- ❌ **Centralized Error Management**: No unified error response format
- ❌ **Recovery Suggestions**: No user-actionable error guidance
- ❌ **Error Categorization**: Missing business logic error types

## Implementation Plan

### Step 1: Domain-Specific Exception Classes
```bash
# Create landscape architecture specific exceptions
mkdir -p src/exceptions
cat > src/exceptions/__init__.py << 'EOF'
"""
Landscape Architecture Tool - Domain-Specific Exceptions
"""
from .base import (
    LandscapeToolException,
    ValidationError,
    BusinessLogicError,
    ResourceNotFoundError,
    AuthorizationError
)
from .plant_exceptions import (
    PlantValidationError,
    PlantCompatibilityError,
    PlantSeasonalError,
    PlantClimateError
)
from .project_exceptions import (
    ProjectValidationError,
    ProjectBudgetError,
    ProjectTimelineError,
    ProjectResourceError
)
from .supplier_exceptions import (
    SupplierValidationError,
    SupplierAvailabilityError,
    SupplierPricingError
)

__all__ = [
    'LandscapeToolException',
    'ValidationError',
    'BusinessLogicError',
    'ResourceNotFoundError',
    'AuthorizationError',
    'PlantValidationError',
    'PlantCompatibilityError',
    'PlantSeasonalError',
    'PlantClimateError',
    'ProjectValidationError',
    'ProjectBudgetError',
    'ProjectTimelineError',
    'ProjectResourceError',
    'SupplierValidationError',
    'SupplierAvailabilityError',
    'SupplierPricingError'
]
EOF

cat > src/exceptions/base.py << 'EOF'
"""
Base exception classes for Landscape Architecture Tool
"""
from typing import Dict, Any, Optional, List

class LandscapeToolException(Exception):
    """Base exception for all landscape tool errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None,
        details: Dict[str, Any] = None,
        recovery_suggestions: List[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.recovery_suggestions = recovery_suggestions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            'error': self.error_code,
            'message': self.message,
            'details': self.details,
            'recovery_suggestions': self.recovery_suggestions,
            'error_type': self.__class__.__name__
        }

class ValidationError(LandscapeToolException):
    """Data validation errors."""
    
    def __init__(self, field: str, value: Any, message: str = None):
        self.field = field
        self.value = value
        msg = message or f"Invalid value for field '{field}': {value}"
        super().__init__(
            message=msg,
            error_code="VALIDATION_ERROR",
            details={'field': field, 'value': str(value)},
            recovery_suggestions=[
                f"Check the format and constraints for field '{field}'",
                "Refer to the API documentation for valid values"
            ]
        )

class BusinessLogicError(LandscapeToolException):
    """Business logic constraint violations."""
    
    def __init__(self, operation: str, reason: str, context: Dict[str, Any] = None):
        self.operation = operation
        self.reason = reason
        self.context = context or {}
        
        super().__init__(
            message=f"Cannot {operation}: {reason}",
            error_code="BUSINESS_LOGIC_ERROR",
            details={'operation': operation, 'reason': reason, **self.context},
            recovery_suggestions=[
                "Review the business rules for this operation",
                "Check if prerequisites are met",
                "Contact support if the constraint seems incorrect"
            ]
        )

class ResourceNotFoundError(LandscapeToolException):
    """Resource not found errors."""
    
    def __init__(self, resource_type: str, identifier: Any):
        self.resource_type = resource_type
        self.identifier = identifier
        
        super().__init__(
            message=f"{resource_type} with identifier '{identifier}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details={'resource_type': resource_type, 'identifier': str(identifier)},
            recovery_suggestions=[
                f"Verify the {resource_type.lower()} identifier is correct",
                f"Check if the {resource_type.lower()} has been deleted",
                "Use the list endpoint to find available resources"
            ]
        )

class AuthorizationError(LandscapeToolException):
    """Authorization and permission errors."""
    
    def __init__(self, action: str, resource: str = None):
        self.action = action
        self.resource = resource
        
        resource_text = f" on {resource}" if resource else ""
        super().__init__(
            message=f"Not authorized to {action}{resource_text}",
            error_code="AUTHORIZATION_ERROR",
            details={'action': action, 'resource': resource},
            recovery_suggestions=[
                "Check your user permissions",
                "Contact an administrator for access",
                "Ensure you are logged in with the correct account"
            ]
        )
EOF
```

### Step 2: Plant-Specific Exceptions
```bash
cat > src/exceptions/plant_exceptions.py << 'EOF'
"""
Plant-specific exceptions for landscape architecture operations
"""
from typing import List, Dict, Any
from .base import LandscapeToolException, ValidationError

class PlantValidationError(ValidationError):
    """Plant data validation errors."""
    
    def __init__(self, field: str, value: Any, botanical_context: str = None):
        self.botanical_context = botanical_context
        super().__init__(
            field=field,
            value=value,
            message=f"Invalid plant {field}: {value}" + 
                   (f" (Context: {botanical_context})" if botanical_context else "")
        )
        if botanical_context:
            self.details['botanical_context'] = botanical_context
        
        self.recovery_suggestions.extend([
            "Verify botanical name follows standard nomenclature",
            "Check plant characteristics against botanical databases",
            "Ensure climate zone data is accurate"
        ])

class PlantCompatibilityError(LandscapeToolException):
    """Plant compatibility and pairing errors."""
    
    def __init__(self, plant1: str, plant2: str, conflict_reason: str):
        self.plant1 = plant1
        self.plant2 = plant2
        self.conflict_reason = conflict_reason
        
        super().__init__(
            message=f"Plants '{plant1}' and '{plant2}' are incompatible: {conflict_reason}",
            error_code="PLANT_COMPATIBILITY_ERROR",
            details={
                'plant1': plant1,
                'plant2': plant2,
                'conflict_reason': conflict_reason
            },
            recovery_suggestions=[
                "Review plant pairing guidelines",
                "Consider alternative plant selections",
                "Adjust spatial planning to separate incompatible plants",
                "Consult botanical compatibility charts"
            ]
        )

class PlantSeasonalError(LandscapeToolException):
    """Plant seasonal availability and timing errors."""
    
    def __init__(self, plant_name: str, requested_season: str, available_seasons: List[str]):
        self.plant_name = plant_name
        self.requested_season = requested_season
        self.available_seasons = available_seasons
        
        super().__init__(
            message=f"Plant '{plant_name}' not available in {requested_season}. "
                   f"Available seasons: {', '.join(available_seasons)}",
            error_code="PLANT_SEASONAL_ERROR",
            details={
                'plant_name': plant_name,
                'requested_season': requested_season,
                'available_seasons': available_seasons
            },
            recovery_suggestions=[
                f"Schedule planting for: {', '.join(available_seasons)}",
                "Consider seasonal alternatives with similar characteristics",
                "Plan project timeline around plant availability",
                "Contact suppliers for extended availability options"
            ]
        )

class PlantClimateError(LandscapeToolException):
    """Plant climate zone compatibility errors."""
    
    def __init__(self, plant_name: str, project_zone: str, plant_zones: List[str]):
        self.plant_name = plant_name
        self.project_zone = project_zone
        self.plant_zones = plant_zones
        
        super().__init__(
            message=f"Plant '{plant_name}' (zones: {', '.join(plant_zones)}) "
                   f"not suitable for project climate zone {project_zone}",
            error_code="PLANT_CLIMATE_ERROR",
            details={
                'plant_name': plant_name,
                'project_zone': project_zone,
                'plant_zones': plant_zones
            },
            recovery_suggestions=[
                "Select plants compatible with your climate zone",
                "Consider microclimate modifications",
                "Use climate-appropriate plant alternatives",
                "Consult local horticultural guidelines"
            ]
        )
EOF
```

### Step 3: Centralized Error Handler
```bash
# Enhanced error handling system
cat > src/core/error_manager.py << 'EOF'
"""
Centralized error management for Landscape Architecture Tool
"""
import logging
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from src.exceptions import LandscapeToolException

logger = logging.getLogger(__name__)

class ErrorManager:
    """Centralized error management and response formatting."""
    
    @staticmethod
    def handle_landscape_exception(error: LandscapeToolException) -> Tuple[Dict[str, Any], int]:
        """Handle domain-specific exceptions."""
        logger.warning(f"Landscape tool error: {error.message}", extra=error.details)
        
        response_data = error.to_dict()
        response_data['success'] = False
        
        # Determine HTTP status code based on error type
        status_code = ErrorManager._get_status_code(error)
        
        return response_data, status_code
    
    @staticmethod
    def handle_http_exception(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle HTTP exceptions."""
        logger.info(f"HTTP error: {error.code} - {error.description}")
        
        return {
            'success': False,
            'error': f"HTTP_{error.code}",
            'message': error.description,
            'details': {},
            'recovery_suggestions': ErrorManager._get_http_recovery_suggestions(error.code)
        }, error.code
    
    @staticmethod
    def handle_generic_exception(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        
        if current_app.debug:
            # In debug mode, provide detailed error information
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': str(error),
                'details': {'exception_type': type(error).__name__},
                'recovery_suggestions': [
                    'This is an internal error - please contact support',
                    'Check the application logs for more details'
                ]
            }, 500
        else:
            # In production, provide generic error message
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'An internal error occurred. Please try again later.',
                'details': {},
                'recovery_suggestions': [
                    'Try the request again in a few moments',
                    'Contact support if the problem persists'
                ]
            }, 500
    
    @staticmethod
    def _get_status_code(error: LandscapeToolException) -> int:
        """Map exception types to HTTP status codes."""
        from src.exceptions import (
            ValidationError, BusinessLogicError, 
            ResourceNotFoundError, AuthorizationError
        )
        
        mapping = {
            ValidationError: 400,
            BusinessLogicError: 422,
            ResourceNotFoundError: 404,
            AuthorizationError: 403
        }
        
        return mapping.get(type(error), 500)
    
    @staticmethod
    def _get_http_recovery_suggestions(status_code: int) -> list:
        """Get recovery suggestions for HTTP status codes."""
        suggestions = {
            400: ["Check request format and required parameters"],
            401: ["Provide valid authentication credentials"],
            403: ["Ensure you have proper permissions"],
            404: ["Verify the resource URL and identifier"],
            405: ["Use the correct HTTP method for this endpoint"],
            429: ["Reduce request frequency", "Try again after the rate limit resets"],
            500: ["Try again later", "Contact support if the problem persists"],
            503: ["The service is temporarily unavailable", "Try again in a few minutes"]
        }
        
        return suggestions.get(status_code, ["Contact support for assistance"])

def register_error_handlers(app):
    """Register error handlers with Flask application."""
    
    @app.errorhandler(LandscapeToolException)
    def handle_landscape_exception(error):
        response_data, status_code = ErrorManager.handle_landscape_exception(error)
        return jsonify(response_data), status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response_data, status_code = ErrorManager.handle_http_exception(error)
        return jsonify(response_data), status_code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        response_data, status_code = ErrorManager.handle_generic_exception(error)
        return jsonify(response_data), status_code
EOF
```

### Step 4: Integration with Service Layer
```bash
# Update base service to use enhanced error handling
cat >> src/services/core/base_service.py << 'EOF'

# Enhanced error handling integration
from src.exceptions import (
    ValidationError, BusinessLogicError, ResourceNotFoundError
)

class EnhancedBaseService(BaseService):
    """Enhanced base service with comprehensive error handling."""
    
    def get_by_id(self, id: int) -> Any:
        """Get record by ID with proper error handling."""
        if not isinstance(id, int) or id <= 0:
            raise ValidationError('id', id, 'ID must be a positive integer')
        
        instance = self.model_class.query.get(id)
        if not instance:
            raise ResourceNotFoundError(self.model_class.__name__, id)
        
        return instance
    
    def create(self, **data) -> Any:
        """Create new record with validation."""
        try:
            # Validate data using business logic
            validated_data = self.validate_data(data)
            
            instance = self.model_class(**validated_data)
            db.session.add(instance)
            db.session.commit()
            return instance
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, LandscapeToolException):
                raise
            raise BusinessLogicError(
                operation=f"create {self.model_class.__name__}",
                reason=str(e),
                context=data
            )
    
    def update(self, id: int, **data) -> Any:
        """Update existing record with validation."""
        instance = self.get_by_id(id)  # This will raise ResourceNotFoundError if not found
        
        try:
            # Validate data using business logic
            validated_data = self.validate_data(data)
            
            for key, value in validated_data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    raise ValidationError(key, value, f'Field does not exist on {self.model_class.__name__}')
            
            db.session.commit()
            return instance
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, LandscapeToolException):
                raise
            raise BusinessLogicError(
                operation=f"update {self.model_class.__name__}",
                reason=str(e),
                context={'id': id, **data}
            )
EOF
```

## Validation Commands

### After Each Step
```bash
# Test exception imports
python -c "
from src.exceptions import (
    PlantValidationError, PlantCompatibilityError,
    ProjectValidationError, SupplierValidationError
)
print('All exception classes imported successfully')
"

# Test error manager
python -c "
from src.core.error_manager import ErrorManager
from src.exceptions import ValidationError

error = ValidationError('test_field', 'invalid_value')
response, code = ErrorManager.handle_landscape_exception(error)
print(f'Error handling works: {response[\"error\"]} - {code}')
"
```

### Final Validation
```bash
# Comprehensive error handling validation
python -c "
from src.exceptions import PlantCompatibilityError
from src.core.error_manager import ErrorManager

# Test plant compatibility error
error = PlantCompatibilityError('Rose', 'Walnut', 'allelopathic conflict')
response, code = ErrorManager.handle_landscape_exception(error)

print('Error Response:')
print(f'- Code: {code}')
print(f'- Error: {response[\"error\"]}')
print(f'- Message: {response[\"message\"]}')
print(f'- Suggestions: {len(response[\"recovery_suggestions\"])} provided')
"
```

## Testing Requirements

### Unit Tests
```bash
# Create comprehensive error handling tests
cat > tests/test_error_handling.py << 'EOF'
"""Tests for enhanced error handling system."""
import pytest
from src.exceptions import (
    PlantValidationError, PlantCompatibilityError,
    ValidationError, BusinessLogicError
)
from src.core.error_manager import ErrorManager

def test_plant_validation_error():
    """Test plant validation error creation and formatting."""
    error = PlantValidationError('botanical_name', 'invalid name', 'nomenclature')
    response, code = ErrorManager.handle_landscape_exception(error)
    
    assert code == 400
    assert response['error'] == 'VALIDATION_ERROR'
    assert 'botanical_context' in response['details']
    assert len(response['recovery_suggestions']) > 3

def test_plant_compatibility_error():
    """Test plant compatibility error handling."""
    error = PlantCompatibilityError('Rose', 'Walnut', 'allelopathic conflict')
    response, code = ErrorManager.handle_landscape_exception(error)
    
    assert code == 500  # Default for LandscapeToolException
    assert 'plant1' in response['details']
    assert 'plant2' in response['details']
    assert 'botanical compatibility' in str(response['recovery_suggestions'])

def test_error_to_dict():
    """Test error dictionary conversion."""
    error = ValidationError('test_field', 'test_value')
    error_dict = error.to_dict()
    
    required_keys = ['error', 'message', 'details', 'recovery_suggestions', 'error_type']
    for key in required_keys:
        assert key in error_dict
EOF

# Run error handling tests
PYTHONPATH=. python -m pytest tests/test_error_handling.py -v
```

### Integration Tests
```bash
# Test with Flask application
PYTHONPATH=. python -c "
from src.core.app_factory import create_app
from src.exceptions import ValidationError
from flask import Flask

app = create_app('testing')

# Test error handler registration
with app.app_context():
    # This would trigger error handler in real request
    error = ValidationError('test', 'value')
    print(f'Error handler ready for: {error.error_code}')
"
```

## Success Criteria

- [ ] Domain-specific exception classes created for plants, projects, suppliers
- [ ] Centralized error management system operational
- [ ] Recovery suggestions provided for all error types
- [ ] Integration with service layer completed
- [ ] Comprehensive error response format standardized
- [ ] All error handling tests passing
- [ ] Backward compatibility maintained

## Dependencies for Next Issues

This issue enables:
- **Issue 04**: API Versioning (requires standardized error responses)
- **Issue 05**: Caching Strategy (requires error handling for cache failures)
- **Issue 12**: Plant Database Enhancement (requires plant-specific exceptions)

## Copilot Automation Instructions

1. Create exception hierarchy starting with base classes
2. Implement domain-specific exceptions for landscape architecture
3. Build centralized error manager with recovery suggestions
4. Integrate error handling with service layer
5. Test all error scenarios with comprehensive validation
6. Ensure existing functionality continues to work

**Estimated Implementation Time**: 6-10 hours including comprehensive testing