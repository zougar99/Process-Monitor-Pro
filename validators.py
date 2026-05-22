"""
Input validation utilities
"""

import re
from typing import Optional, Tuple, Union


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, None  # Email is optional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, None
    else:
        return False, "Invalid email format"


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number (Moroccan format)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return True, None  # Phone is optional
    
    # Remove non-digits
    digits = ''.join(filter(str.isdigit, phone))
    
    # Moroccan phone: 10 digits starting with 0, or 12 digits starting with 212
    if len(digits) == 10 and digits.startswith('0'):
        return True, None
    elif len(digits) == 12 and digits.startswith('212'):
        return True, None
    elif len(digits) == 9:  # Without leading 0
        return True, None
    
    return False, "Invalid phone number format (expected: 0XXXXXXXXX or +212XXXXXXXXX)"


def validate_required(value: any, field_name: str = "Field") -> Tuple[bool, Optional[str]]:
    """
    Validate required field
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error message)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} is required"
    return True, None


def validate_positive_number(value: Union[float, int], field_name: str = "Value") -> Tuple[bool, Optional[str]]:
    """
    Validate positive number
    
    Args:
        value: Number to validate
        field_name: Name of the field (for error message)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, f"{field_name} is required"
    
    try:
        num = float(value)
        if num < 0:
            return False, f"{field_name} must be positive"
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


def validate_code(code: str, field_name: str = "Code") -> Tuple[bool, Optional[str]]:
    """
    Validate code format (alphanumeric, dashes, underscores)
    
    Args:
        code: Code to validate
        field_name: Name of the field (for error message)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return False, f"{field_name} is required"
    
    pattern = r'^[A-Za-z0-9_-]+$'
    if re.match(pattern, code):
        return True, None
    else:
        return False, f"{field_name} can only contain letters, numbers, dashes, and underscores"


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date range (end_date must be after start_date)
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from core.formatters import parse_date
    
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if not start or not end:
        return False, "Invalid date format"
    
    if end < start:
        return False, "End date must be after start date"
    
    return True, None


def validate_credit_limit(credit_limit: float, balance: float = 0) -> Tuple[bool, Optional[str]]:
    """
    Validate credit limit (balance should not exceed limit)
    
    Args:
        credit_limit: Credit limit amount
        balance: Current balance
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if credit_limit < 0:
        return False, "Credit limit cannot be negative"
    
    if balance > credit_limit:
        return False, f"Balance ({balance}) exceeds credit limit ({credit_limit})"
    
    return True, None
