def format_usd(amount):
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"