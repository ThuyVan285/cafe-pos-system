# FILE: utils/validator.py
from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    message: str = ""

    def __bool__(self) -> bool:
        return self.valid


def validate_quantity(quantity: int) -> ValidationResult:
    if quantity < 1:
        return ValidationResult(False, "Quantity must be at least 1.")
    if quantity > 99:
        return ValidationResult(False, "Quantity cannot exceed 99.")
    return ValidationResult(True)


def validate_price(price: int) -> ValidationResult:
    if price < 0:
        return ValidationResult(False, "Price cannot be negative.")
    return ValidationResult(True)


def validate_product_name(name: str) -> ValidationResult:
    name = name.strip()
    if not name:
        return ValidationResult(False, "Product name is required.")
    if len(name) > 100:
        return ValidationResult(False, "Product name is too long (max 100 chars).")
    return ValidationResult(True)


def validate_payment_amount(received: int, total: int) -> ValidationResult:
    if received < total:
        return ValidationResult(False, f"Amount received is less than total ({total:,}).")
    return ValidationResult(True)


def validate_table_merge(table_a_id: int, table_b_id: int) -> ValidationResult:
    if table_a_id == table_b_id:
        return ValidationResult(False, "Cannot merge a table with itself.")
    return ValidationResult(True)