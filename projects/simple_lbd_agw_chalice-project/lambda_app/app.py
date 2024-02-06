# -*- coding: utf-8 -*-

from chalice import Chalice, AuthResponse
from simple_lbd_agw_chalice.config.api import config
from simple_lbd_agw_chalice.lbd import hello
from simple_lbd_agw_chalice.lbd import add_one

# define a Chalice app
app = Chalice(app_name=config.env.chalice_app_name)


# a pure native lambda function
@app.lambda_function(name=config.env.lbd_hello.short_name)
def handler_hello(event, context):
    return hello.lambda_handler(event, context)


# even though we already have a rest API handler, we want to have a pure lambda
# function version of it for testing without using API gateway
@app.lambda_function(name=config.env.lbd_add_one.short_name)
def handler_add_one(event, context):
    return add_one.handler(event, None)


@app.authorizer()
def demo_auth(auth_request):
    """
    Implement custom Authorization logic

    More details about built-in Custom Authorizer integration with Chalice
    can be found at https://aws.github.io/chalice/topics/authorizers.html?highlight=authorizer#built-in-authorizers
    """
    token = auth_request.token
    if token == config.env.auth_token:
        return AuthResponse(routes=["*"], principal_id="user")
    else:
        # By specifying an empty list of routes,
        # we're saying this user is not authorized
        # for any URLs, which will result in an
        # Unauthorized response.
        return AuthResponse(routes=[], principal_id="user")


# define an API endpoint powered by AWS Lambda
@app.route(
    "/",
    methods=[
        "GET",
    ],
    name="index",
    authorizer=demo_auth,
)
def index():
    return {"message": "Hello World!"}


@app.route(
    "/user",
    methods=[
        "POST",
    ],
    name="user",
    authorizer=demo_auth,
)
def hello_user():
    # expect {"name": "alice"}
    event = app.current_request.json_body
    return hello.lambda_handler(event, None)


@app.route(
    "/incr",
    methods=[
        "POST",
    ],
    content_types=[
        "application/json",
    ],
    name="incr",
    authorizer=demo_auth,
)
def incr():
    # expect {"key": "some_key"}
    event = app.current_request.json_body
    response = add_one.handler(event, None)
    return response
