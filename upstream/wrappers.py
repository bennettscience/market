from functools import wraps
from flask import request, render_template

def templated(template=None):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			template_name = template
			ctx = f(*args, **kwargs)
			if request.htmx:
				resp = render_template(template_name, **ctx)
			else:
				resp = render_template(
					"shared/layout-wrap.html", 
					partial=template_name, 
					data=ctx
				)
			return resp
		return decorated_function
	return decorator
