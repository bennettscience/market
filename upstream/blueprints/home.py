from flask import abort, current_app, Blueprint, redirect, render_template, session
from flask_login import current_user
from htmx_flask import make_response, request
from webargs import fields
from webargs.flaskparser import parser

from flask_login import login_user
from upstream.models import Event, User
from upstream.schemas import EventSchema

bp = Blueprint("home", __name__)


@bp.get("/")
def index():
    if not current_user.is_anonymous:
        
        events = Event.query.order_by(Event.starts.desc()).all()
        template = "home/index.html"

        resp_data = {
            "events": EventSchema(many=True).dump(events)
        }

        if request.htmx:
            resp = render_template(template, **resp_data)
        else:
            resp = render_template("shared/layout-wrap.html", partial=template, data=resp_data)

        return resp
    else:
        template = "home/login.html"
        if request.htmx:
            resp = render_template(template)
        else:
            resp = render_template("shared/layout-wrap.html", partial=template, data={})
    
        return resp

@bp.get("/login")
def login():
    args = parser.parse({"login_token": fields.Str()}, location="querystring")
    if not args['login_token']:
        abort(403)
    elif args['login_token'] != current_app.config.get('LOGIN_TOKEN'):
        abort(403)
    elif args['login_token'] == current_app.config.get('LOGIN_TOKEN'):
        user = User.query.filter(User.name == "upstream").first()
        login_user(user, remember=True)

        return make_response(
            redirect('/'),
            refresh=True,
            trigger={"showToast": "Successfully logged in!"}
        )

@bp.get("/stats")
def all_stats():
    pass
