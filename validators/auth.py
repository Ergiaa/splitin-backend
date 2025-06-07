from flask_restful import reqparse

# POST /auth
post_parser = reqparse.RequestParser()
post_parser.add_argument('email', type=str, location=['json', 'form'], required=True, help="`email` is required")
post_parser.add_argument('password', type=str, location=['json', 'form'], required=True, help="`password` is required")