import csv

FORMULA_TRIGGERS = ('=', '+', '-', '@', '|')

class Echo:
    @staticmethod
    def write(value):
        return value


def generate_user_permission_sets_csv_rows(users):
    writer = csv.writer(Echo())
    yield writer.writerow(
        ["User ID", "Permission Set", "Gives Global Access", "Permissions"]
    )
    for user in users:
        permission_sets = user.permission_sets.all()
        if permission_sets:
            for ps in permission_sets:
                yield writer.writerow(
                    sanitise_row([user.user_id, ps.display_name, ps.global_access, ps.name])
                )
        else:
            yield writer.writerow(sanitise_row([user.user_id, "", "", ""]))

def sanitise_row(row):
    sanitised_row = []
    for cell in row:
        cell_str = str(cell)
        if cell_str.startswith(FORMULA_TRIGGERS):
            sanitised_row.append(f"'{cell_str}")
        else:
            sanitised_row.append(cell_str)
    return sanitised_row