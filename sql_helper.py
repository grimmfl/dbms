from typing import List


def get_selected_columns(sql: str) -> List[str]:
    """
    Gets the selected columns for a select command.\n
    :param sql: The command
    :return: The selected columns
    """
    sql = sql.lower()
    if "select" not in sql:
        raise ValueError("Not a select command.")
    select_index = sql.find("select") + 6
    sql = sql[select_index:].strip()
    splitted = sql.split(",")
    splitted = [c.strip() for c in splitted]
    columns = []
    for entry in splitted:
        if " " in entry:
            columns.append(entry.split(" ")[0])
            break
        else:
            columns.append(entry)
    return columns

