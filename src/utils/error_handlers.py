import logging
from functools import wraps

from flask import jsonify
from pydantic import ValidationError
from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class LandscapeError(Exception):
    """Base exception for landscape application"""

    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = {"error": self.message}
        if self.payload:
            result.update(self.payload)
        return result


class LandscapeValidationError(LandscapeError):
    """Exception for validation errors"""

    def __init__(self, message, errors=None):
        super().__init__(
            message, status_code=400, payload={"validation_errors": errors}
        )


class NotFoundError(LandscapeError):
    """Exception for resource not found"""

    def __init__(self, resource, resource_id=None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with ID {resource_id}"
        super().__init__(message, status_code=404)


class DatabaseError(LandscapeError):
    """Exception for database operations"""

    def __init__(self, message):
        super().__init__(f"Database error: {message}", status_code=500)


def handle_validation_error(error):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {error}")

    if isinstance(error, ValidationError):
        errors = []
        for err in error.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
            )

        return (
            jsonify({"error": "Validation failed", "validation_errors": errors}),
            400,
        )

    return jsonify({"error": str(error)}), 400


def handle_landscape_error(error):
    """Handle custom landscape errors"""
    logger.error(f"Landscape error: {error.message}")
    return jsonify(error.to_dict()), error.status_code


def handle_generic_error(error):
    """Handle generic exceptions"""
    logger.error(f"Unexpected error: {str(error)}")
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


def register_error_handlers(app):
    """Register error handlers with Flask app"""

    @app.errorhandler(ValidationError)
    def validation_error_handler(error):
        return handle_validation_error(error)

    @app.errorhandler(LandscapeError)
    def landscape_error_handler(error):
        return handle_landscape_error(error)

    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error_handler(error):
        return handle_generic_error(error)

    @app.errorhandler(Exception)
    def generic_error_handler(error):
        return handle_generic_error(error)


def handle_errors(f):
    """Decorator for handling errors in route functions with improved specificity"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except LandscapeError as e:
            logger.info(f"Business logic error in {f.__name__}: {str(e)}")
            return handle_landscape_error(e)
        except ValidationError as e:
            logger.info(f"Validation error in {f.__name__}: {str(e)}")
            return handle_validation_error(e)
        except IntegrityError as e:
            logger.warning(f"Database integrity error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Data integrity violation",
                        "message": "The operation conflicts with existing data",
                    }
                ),
                409,
            )
        except DataError as e:
            logger.warning(f"Database data error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Invalid data format",
                        "message": "The provided data format is invalid",
                    }
                ),
                400,
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Database error",
                        "message": "A database operation failed",
                    }
                ),
                500,
            )
        except HTTPException as e:
            logger.info(f"HTTP exception in {f.__name__}: {e.code} - {e.description}")
            raise  # Let Flask handle HTTP exceptions
        except KeyError as e:
            logger.warning(f"Missing key error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Missing required field",
                        "message": "One or more required fields are missing.",
                    }
                ),
                400,
            )
        except TypeError as e:
            logger.warning(f"Type error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Invalid data type",
                        "message": "One or more fields have invalid data types",
                    }
                ),
                400,
            )
        except ValueError as e:
            logger.warning(f"Value error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Invalid value", "message": str(e)}), 400
        except Exception as e:
            logger.error(
                f"Unexpected error in {f.__name__}: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            return handle_generic_error(e)

    return wrapper
