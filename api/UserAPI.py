from flask import request, jsonify
from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.model import db, User

user_post_args = reqparse.RequestParser()
user_post_args.add_argument('user_mail', type=str)
user_post_args.add_argument('password', type=str)
user_post_args.add_argument('role', type=str)

resource_fields = {
    'user_id': fields.Integer,
    'user_mail': fields.String,
    'password': fields.String,
    'user_name':fields.String,
    'profile_img_path':fields.String,
    'role':fields.String
}


class AllUserAPI(Resource):
    def get(resource):
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({'user_id': user.user_id,'user_mail': user.user_mail,'user_name':user.user_name,'profile_img_path':user.profile_img_path,'role':user.role})
        return user_list

    def post(resource):
        args = user_post_args.parse_args()
        user = User.query.filter_by(user_mail = args["user_mail"]).first()
        if user:
            abort(409,message="user mail already registered")
        new_user = User(email= args["user_mail"], password=args["password"], role=args["role"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'status':'success', 'message':'user added'})
    
class UserAPI(Resource):
    @marshal_with(resource_fields)
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        return user, 200

    @marshal_with(resource_fields)
    def put(self, user_id):
        args = user_post_args.parse_args()
        user = User.query.filter_by(user_id = user_id).first()
        if not user:
            abort(404, message="this user is not in database")
        if args["user_mail"]:
            user.user_mail = args["user_mail"]
        if args["password"]:
            user.password = args["password"]
        if args["role"]:
            user.password = args["role"]
        db.session.commit()
        return user


    def delete(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'Deleted', 'message':"User is deleted"})

    