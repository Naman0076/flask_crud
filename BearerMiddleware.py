from werkzeug.wrappers import Request, Response

class BearerMiddleware:
    def __init__(self, app, valid_token):
        self.app = app
        self.valid_token = valid_token

    def __call__(self, environ, start_response):
        request = Request(environ)
        auth_header = request.headers.get("Authorization")

        # Check if Authorization header is provided
        if not auth_header or not auth_header.startswith("Bearer "):
            res = Response("Missing or invalid token", mimetype='text/plain', status=401)
            return res(environ, start_response)

        # Extract and validate token
        token = auth_header.split(" ")[1]
        if token != self.valid_token:
            res = Response("Unauthorized: Invalid token", mimetype='text/plain', status=401)
            return res(environ, start_response)

        # Store user info in request environment
        environ["user"] = {"name": "Authorized User"}
        return self.app(environ, start_response)
