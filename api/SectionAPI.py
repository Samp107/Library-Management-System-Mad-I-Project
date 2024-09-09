from flask import request, jsonify
from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.model import db, Section

section_post_args = reqparse.RequestParser()
section_post_args.add_argument('section_name', type=str)


resource_fields = {
    'section_id': fields.Integer,
    'section_name': fields.String,
}


class AllSectionAPI(Resource):
    def get(resource):
        sections = Section.query.all()
        section_list = []
        for section in sections:
            section_list.append({'section_id': section.section_id,'section_name':section.section_name})
        return section_list

    def post(resource):
        args = section_post_args.parse_args()
        section = Section.query.filter_by(section_name = args["section_name"]).first()
        if section:
            abort(409,message="section already added")
        new_section = Section(name = args["section_name"])
        db.session.add(new_section)
        db.session.commit()
        return jsonify({'status':'success', 'message':'section added'})
    
class SectionAPI(Resource):
    @marshal_with(resource_fields)
    def get(self, section_id):
        section = Section.query.filter_by(section_id = section_id).first()
        return section, 200

    @marshal_with(resource_fields)
    def put(self, section_id):
        args = section_post_args.parse_args()
        section = Section.query.filter_by(section_id = section_id).first()
        if not section:
            abort(404, message="this section is not in database")
        if args["section_name"]:
            section.section_name = args["section_name"]
        
        db.session.commit()
        return section


    def delete(self, section_id):
        section = Section.query.filter_by(section_id = section_id).first()
        db.session.delete(section)
        db.session.commit()
        return jsonify({'status': 'Deleted', 'message':"Section is deleted"})

    