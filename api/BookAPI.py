from flask import request, jsonify
from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.model import db, Book

book_post_args = reqparse.RequestParser()
book_post_args.add_argument('book_title', type=str)
book_post_args.add_argument('Author', type=str)
book_post_args.add_argument('section_name', type=str)
book_post_args.add_argument('book_price', type=int)

resource_fields = {
    'book_id':fields.Integer,
    'book_title': fields.String,
    'Author': fields.String,
    'section_name': fields.String,
    'book_img_path':fields.String,
    'book_pdf_path':fields.String,
    'book_price':fields.Integer
}


class AllBookAPI(Resource):
    def get(resource):
        books = Book.query.all()
        book_list = []
        for book in books:
            book_list.append({'book_id': book.book_id,'book_title': book.book_title,'Author': book.Author,
                            'section_name':book.section_name,'book_img_path':book.book_img_path,'book_pdf_path':book.book_pdf_path,'book_price':book.book_price})
        return book_list

    def post(resource):
        args = book_post_args.parse_args()
        book = Book.query.filter_by(book_title = args["book_title"]).first()
        if book:
            abort(409,message="book already exists")
        new_book = Book(book_title= args["book_title"], Author=args["Author"], section_name=args["section_name"], book_price = args["book_price"], 
                    book_img_path = args["book_img_path"], book_pdf_path = args["book_pdf_path"], book_content = args["book_content"], date_added=args["date_added"] )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'status':'success', 'message':'book added'})
    
class BookAPI(Resource):
    @marshal_with(resource_fields)
    def get(self, book_id):
        book = Book.query.filter_by(book_id=book_id).first()
        return book, 200

    @marshal_with(resource_fields)
    def put(self, book_id):
        args = book_post_args.parse_args()
        book = Book.query.filter_by(book_id=book_id).first()
        if not book:
            abort(404, message="this book is not in database")
        if args["book_title"]:
            book.book_title = args["book_title"]
        if args["Author"]:
            book.Author = args["Author"]
        if args["section_name"]:
            book.section_name = args["section_name"]
        if args["book_price"]:
            book.book_price = args["book_price"]
        db.session.commit()
        return book


    def delete(self, book_id):
        book = Book.query.filter_by(book_id=book_id).first()
        db.session.delete(book)
        db.session.commit()
        return jsonify({'status': 'Deleted', 'message':"Book is deleted"})

    