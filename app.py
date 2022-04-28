from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__, template_folder='templates')
app.config['MONGO_URI'] = 'mongodb://localhost'

mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template("sign_up.html")


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
