from flask import Blueprint, redirect, render_template
from flask_login import current_user, login_user, logout_user
from webargs import fields
from webargs.flaskparser import parser

from upstream.extensions import db
from upstream.models import User

bp = Blueprint("user", __name__)


@bp.route("/users/<string:name>")
def create(name):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()

    return "Created user!"

@bp.post("/login")
def login():
    args = parser.parse({
        "name": fields.Str(),
        "password": fields.Str()
    }, location="form")

    user = User.query.filter(User.name == args['name']).first()

    if not user:
        return render_template('home/login.html')
    else:
        login_user(user)
        return redirect('/')

@bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        return render_template('home/register.html')

@bp.post("/register")
def create_user():
    args = parser.parse({
        "name": fields.Str(),
        "password": fields.Str(),
        "password-repeat": fields.Str()
        }, location="form")
    
    user = User.query.filter(User.name == args['name']).first()
    if user:
        return render_template('home/register.html', name=args['name'])
    else:
        if args["password"] == args["password-repeat"]:
            user = User(
                name=args['name'],
            )
            
            user.set_password(args['password'])
            db.session.add(user)
            db.session.commit()

            login_user(user)
            return render_template('home/index.html')
        else:
            return "Your passwords do not match."

@bp.get("/logout")
def logout():
    logout_user()
    return redirect('/')