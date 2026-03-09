def validate_amount(amount):
    numbers = re.findall(r'\d+\.?\d*', amount)
    if numbers:
        return True
    return False