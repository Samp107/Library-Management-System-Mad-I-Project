from flask import Flask, request, render_template
from application.database import db
from flask_restful import Api
from application.model import *
import os
from application.config import LocalDevelopmentConfig
from flask_bcrypt import Bcrypt
from api.UserAPI import AllUserAPI, UserAPI
from api.BookAPI import AllBookAPI, BookAPI
from api.SectionAPI import AllSectionAPI, SectionAPI

app = None

def addadmin():
    if User.query.filter_by(role='admin').first() is None:

        user = User(email = 'admin@gmail.com', password = bcrypt.generate_password_hash('12345',10), role ='admin')
        db.session.add(user)
        db.session.commit()



def create_app():
    app = Flask(__name__, template_folder="Templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()  
    return app 



app = create_app()

api = Api(app)
api.init_app(app)

app.secret_key="123456789"



from application.controllers import *

api.add_resource(AllUserAPI, '/api/user')
api.add_resource(UserAPI,'/api/user/<int:user_id>')

api.add_resource(AllBookAPI, '/api/book')
api.add_resource(BookAPI,'/api/book/<int:book_id>')

api.add_resource(AllSectionAPI, '/api/section')
api.add_resource(SectionAPI,'/api/section/<int:section_id>')

with app.app_context():
    db.create_all()
    addadmin()




if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000, debug=True)