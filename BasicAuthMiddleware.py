import base64
from werkzeug.wrappers import Request, Response

class BasicAuthMiddleware:
    def __init__(self, app, valid_username, valid_password):
        self.app = app
        self.valid_username = valid_username
        self.valid_password = valid_password

    def __call__(self, environ, start_response):
        request = Request(environ)
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            res = Response("Missing or invalid authentication", mimetype='text/plain', status=401)
            res.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
            return res(environ, start_response)

        # Extract username and password
        try:
            auth_decoded = base64.b64decode(auth_header.split(" ")[1]).decode("utf-8")
            username, password = auth_decoded.split(":", 1)
        except Exception:
            res = Response("Malformed authentication credentials", mimetype='text/plain', status=400)
            return res(environ, start_response)

        # Validate Credentials
        if username != self.valid_username or password != self.valid_password:
            res = Response("Unauthorized: Invalid credentials", mimetype='text/plain', status=401)
            return res(environ, start_response)

        # Store user info in request environment
        environ["user"] = {"name": username}
        return self.app(environ, start_response)
