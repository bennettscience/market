import unittest

from multiprocessing import context
from contextlib import contextmanager
from flask import template_rendered
from flask_login.utils import login_user


class TestBase(unittest.TestCase):
    """
    Set the base class to easily manage user logins during testing.
    All test classes requiring logins inherit this class.
    """

    @app.route("/auto_login/<user_name>")
    def auto_login(user_name):
        user = User.query.filter(User.name == user_name).first()
        login_user(user, remember=True)
        return "ok"

    def login(self, user_name):
        self.client.get(f"/auto_login/{user_name}")
