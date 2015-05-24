__author__ = 'mensur'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#application object and cofiguration
app = Flask(__name__)
app.config.from_object('config')

#sqlalchmey initialization
#db = SQLAlchemy(app)

import routes, models