from app import app
from flask import request, jsonify

def handler(environ, start_response):
    context = app.request_context(environ)
    with context:
        response = app.full_dispatch_request()
        headers = {k.lower(): v for k, v in response.headers}
        start_response(f'{response.status_code} {response.status}', [(k, v) for k, v in headers.items()])
        return [response.get_data()]