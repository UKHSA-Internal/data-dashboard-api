import csv


class Echo:
    def write(self, value):
        return value


def generate_user_permission_sets_csv_rows(users):
    writer = csv.writer(Echo())
    yield writer.writerow(["User ID", "Permission Set", "Gives Global Access", "Permissions"])
    for user in users:
        permission_sets = user.permission_sets.all()
        if permission_sets:
            for ps in permission_sets:
                yield writer.writerow([user.user_id, ps.display_name, ps.global_access, ps.name])
        else:
            yield writer.writerow([user.user_id, "", ""])
