from flask_restful import reqparse

# POST /users
post_parser = reqparse.RequestParser()
post_parser.add_argument('username', type=str, location=['form'], required=True, help="str `username` is required")
post_parser.add_argument('email', type=str, location=['form'], required=True, help="str `email` is required")
post_parser.add_argument('password', type=str, location=['form'], required=True, help="str `password` is required")

# PATCH /users/{id}
patch_parser = reqparse.RequestParser()
patch_parser.add_argument('name', type=str, location=['form'])
patch_parser.add_argument('email', type=str, location=['form'])
patch_parser.add_argument('student_id', type=str, location=['form'])
patch_parser.add_argument('phone_number', type=str, location=['form'])
