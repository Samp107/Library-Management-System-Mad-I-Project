from .database import db
from flask_login import UserMixin


class User(db.Model,UserMixin):
    __tablename__=  "user"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_mail =  db.Column(db.String(30), nullable = False, unique = True)
    password = db.Column(db.String(80), nullable = False)
    user_name = db.Column(db.String())
    profile_img_path = db.Column(db.String(), default ="static\Images\dummy.jpg")
    role = db.Column(db.String(128), default='user', nullable=False)


    def __init__(self,email,password, role):
        self.user_mail = email
        self.password = password
        self.user_name = email.split('@')[0]
        self.role = role
    
    def get_id(self):
        return self.user_id



class Section(db.Model):
    __tablename__=  "section"
    section_id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(150), nullable=False, unique = True)
    books = db.relationship('Book', backref = "belongsto", cascade = "all, delete" )
    orders = db.relationship('Cart', backref = "belongs", cascade = "all, delete" )
    
    
    def __init__(self,name):
        self.section_name = name
        


class Book(db.Model):
    __tablename__=  "book"
    book_id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(800), nullable=False)
    Author = db.Column(db.String(50))
    book_img_path = db.Column(db.String(800))
    book_pdf_path = db.Column(db.String(800))
    book_content = db.Column(db.String())
    section_name = db.Column(db.String(), db.ForeignKey('section.section_name'))
    book_price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime())
    
    

    def __init__(self, book_title, Author, book_img_path, book_pdf_path,
                  book_content, section_name, book_price, date_added):
        self.book_title = book_title
        self.Author = Author
        self.book_img_path = book_img_path
        self.book_pdf_path = book_pdf_path
        self.book_content = book_content
        self.section_name = section_name
        self.book_price = book_price
        self.date_added = date_added
        
    

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    book_title = db.Column(db.String, db.ForeignKey('book.book_title'), nullable=False)
    section_name = db.Column(db.String(), db.ForeignKey('section.section_name'))
    book_price = db.Column(db.Float, db.ForeignKey('book.book_price'), nullable=False)
    paid = db.Column(db.String, default = 'No')
    status = db.Column(db.Integer, default = 0, nullable=False)
    date_issued = db.Column(db.DateTime(), default=None)
    date_return = db.Column(db.DateTime(), default=None)
    

    def __init__(self, user_id, book_id, section_name, book_title, book_price, 
                        paid = 'NO',status = 0, date_issued = None, date_return = None):
        self.user_id = user_id
        self.book_id = book_id
        self.section_name = section_name
        self.book_title = book_title
        self.book_price = book_price
        self.paid = paid
        self.status = status
        self.date_issued = date_issued
        self.date_return = date_return

    
    def save_book(self):
        db.session.add(self)
        db.session.commit()

    def delete_book(self):
        db.session.delete(self)
        db.session.commit()

