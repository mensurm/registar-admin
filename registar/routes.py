__author__ = 'mensur'

from registar import app


@app.route('/')
def index():
    return 'Home page'
