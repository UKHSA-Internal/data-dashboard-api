AGE_BANDING_DELIMITER = "-"
AGE_GREATER_THAN_OPERATOR = "+"
EXPECTED_AGE_GREATER_THAN_LENGTH = 3
EXPECTED_AGE_BANDING_LENGTH = 5
EXPECTED_AGE_ALL_VALUE = "all"
EXPECTED_DOUBLE_DIGIT_LENGTH = 2


def validate_age(*, age: str) -> str:
    """Validates the `age` value to check it conforms to an allowable structure

    Notes:
        The `age` value must be one of the following:
            - The literal string "all"
            - An age banding e.g. `00-04`
                which must have 2 double-digit numbers
            - An age greater than e.g. `85+`
                which must have 1 double-digit number
                followed by the `+` operator

    Args:
        age: The `age` value being validated

    Returns:
        The input `age` unchanged if
        it has passed the validation checks.

    Raises:
        `ValueError`: If any of the validation checks fail

    """
    if age.isalpha():
        return _validate_age_is_all_value(age=age)

    if AGE_BANDING_DELIMITER in age:
        return _validate_age_banding(age=age)

    if AGE_GREATER_THAN_OPERATOR in age:
        return _validate_age_older_than(age=age)

    raise ValueError


def _validate_age_is_all_value(*, age: str) -> str:
    if age == EXPECTED_AGE_ALL_VALUE:
        return age
    raise ValueError


def _validate_age_banding(*, age: str) -> str:
    if len(age) != EXPECTED_AGE_BANDING_LENGTH:
        raise ValueError

    if age[2] != AGE_BANDING_DELIMITER:
        raise ValueError

    first_number, second_number = age.split(AGE_BANDING_DELIMITER)

    _validate_number_is_double_digit(number=first_number)
    _validate_number_is_double_digit(number=second_number)
    _validate_age_banding_is_in_correct_order(
        left_side_number=int(first_number), right_side_number=int(second_number)
    )

    return age


def _validate_age_older_than(*, age: str) -> str:
    age: str = _validate_age_older_than_ends_with_plus_operator(age=age)
    age_number, _ = age.split(AGE_GREATER_THAN_OPERATOR)
    return _validate_number_is_double_digit(number=age_number)


def _validate_number_is_double_digit(*, number: str) -> str:
    if number.isdigit() and len(number) == EXPECTED_DOUBLE_DIGIT_LENGTH:
        return number
    raise ValueError


def _validate_age_banding_is_in_correct_order(
    *, left_side_number: int, right_side_number: int
) -> None:
    if left_side_number >= right_side_number:
        raise ValueError


def _validate_age_older_than_ends_with_plus_operator(*, age: str) -> str:
    if (
        age.endswith(AGE_GREATER_THAN_OPERATOR)
        and len(age) == EXPECTED_AGE_GREATER_THAN_LENGTH
    ):
        return age
    raise ValueError
