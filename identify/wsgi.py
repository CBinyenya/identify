from werkzeug.contrib.fixers import ProxyFix
from identify import app
app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
	app.run(debug=True)