from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash

app = Flask(__name__)


# Create app
def create_app():
    app.config['MONGO_DBNAME'] = 'finalproject'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017'

    mongo = PyMongo(app)

    from .auth import auth
    from .views import views

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    return app


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id, name, username, email, dob, password):
        self.id = id
        self.name = name
        self.username = username
        self.email = email
        self.dob = dob
        self.password = password


class Listing():
    def _init__(self, uid, listing_id, street, city, state, zip, bed, bath, rent):
        self.user_id = uid
        self.listing_id = listing_id
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        self.bedrooms = bed
        self.bathrooms = bath
        self.rent = rent
