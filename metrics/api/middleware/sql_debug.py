from django.db import connection


def _print_sql(execute, sql, params, many, context):
    print(f"\n[SQL] {sql}")
    if params:
        print(f"[PARAMS] {params}")
    return execute(sql, params, many, context)


class SQLDebugMiddleware:
    """
    Middleware that prints the raw SQL and params for every DB query made
    during a request/response cycle.

    Only intended for local development — add to MIDDLEWARE in local.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with connection.execute_wrapper(_print_sql):
            return self.get_response(request)
