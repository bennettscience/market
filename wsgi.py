import logging
import os
from config import Config
from dotenv import load_dotenv

for env_file in ('.env', '.flaskenv'):
	env = os.path.join(os.getcwd(), env_file)
	if os.path.exists(env):
		load_dotenv(env)

from upstream import create_app

app = create_app(Config)

# logs to the local logger.
if __name__ != '__main__':
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

# Handle running the script locally
if __name__ == '__main__':
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)
	app.run()