__author__ = 'mensur'

from admin.models import db
from admin import app


db.drop_all()
db.create_all()



