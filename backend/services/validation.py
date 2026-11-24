
from datetime import datetime
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
import re

CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("9999999999.99")





def validate_expiry_days(value):

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            "Invitation expiry must be a whole number of days."
        )

    if value <= 0:
        raise ValueError(
            "Invitation expiry must be positive."
        )

    return value


def validate_invitation_token(token):

    if not isinstance(token, str):
        raise ValueError("Invalid invitation token.")

    # Generated tokens use URL-safe characters.
    # token_urlsafe(32) produces a 43-character token.
    if not re.fullmatch(r"[A-Za-z0-9_-]{20,128}", token):
        raise ValueError("Invalid invitation token.")

    return token



def validate_amount(value, field_name="Amount"):

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field_name} must be a valid number.")

    if not amount.is_finite():
        raise ValueError(f"{field_name} must be a finite number.")

    if amount <= 0:
        raise ValueError(f"{field_name} must be positive.")

    if amount > MAX_AMOUNT:
        raise ValueError(f"{field_name} exceeds the maximum allowed amount.")

    if amount != amount.quantize(CENT):
        raise ValueError(
            f"{field_name} can have at most 2 decimal places."
        )

    return amount


def validate_text(
    value,
    field_name="Text",
    max_length=150,
    required=True
):

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")

    value = value.strip()

    if required and not value:
        raise ValueError(f"{field_name} cannot be empty.")

    if not required and not value:
        return None

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} cannot exceed {max_length} characters."
        )

    return value


def validate_datetime(value, field_name="Date"):

    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a valid datetime.")

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            f"{field_name} must include timezone information."
        )

    return value



def validate_date(value, field_name="Date"):

    if value is None:
        return None

    if isinstance(value, datetime) or not isinstance(value, date):
        raise ValueError(
            f"{field_name} must be a valid date."
        )

    return value

