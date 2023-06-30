def object_to_select(items):
    """Unpack a database class for the select partial

    Args:
        items (any): List of database objects

    Returns:
        list (object): [{text, value}, ...] formatted list
    """
    results = [{"text": item.name, "value": item.id} for item in items]
    return results
