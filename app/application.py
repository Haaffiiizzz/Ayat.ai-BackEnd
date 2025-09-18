from main import app


def application(scope, receive, send):
    return app(scope, receive, send)
