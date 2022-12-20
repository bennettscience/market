from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from htmx_flask import make_response
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
        return make_response(
            render_template("home/login-htmx.html"), trigger={"showToast": "Wrong username or password."}
        )
    else:
        login_user(user)
        return make_response("", refresh=True, trigger={"showToast": "Logged in successfully!"})

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
            return render_template('home/index-htmx.html')
        else:
            return "Your passwords do not match."

@bp.get("/logout")
def logout():
    logout_user()
    return redirect('/')