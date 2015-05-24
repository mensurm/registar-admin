__author__ = 'mensur'

#from registar import db
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy import event,inspect
from flask_sqlalchemy import SessionBase
from datetime import datetime
from flask_login import current_user
from uuid import uuid4
import uuid
from flask.ext.security import UserMixin, RoleMixin
from flask_security import current_user



#base class for logging purposes.
class LogBase(AbstractConcreteBase):
    def __iter__(self):
        values = vars(self)
        for attr in self.__mapper__.columns.keys():
            if attr in values:
                yield attr, values[attr]

    def logme(self):
        return dict(self)




class ActiveMixin(LogBase):
    active = db.Column(db.Boolean, default=True, nullable=False, doc=u"If active then record is accessible to authenticated user")

    def set_active(self, active):
        self.active=active

    @staticmethod
    def abefore_delete(mapper, connection, target):
        raise Exception("Delete is not an option!")

    @classmethod
    def trace_active(cls):
        event.listen(cls, 'before_delete', cls.abefore_delete)




class UserBase(AbstractConcreteBase, db.Model):
    # Default fields for Flask-Security
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


    # Additional generic fields
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    real_email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))

    # Confirmable field for Flask-Security
    confirmed_at = db.Column(db.DateTime)

    # Trackable fields for Flask-Security
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer)

    def __iter__(self):
        values = vars(self)
        for attr in self.__mapper__.columns.keys():
            if attr in values:
                yield attr, values[attr]

    def logme(self):
        return dict(self)

    def __unicode__(self):
        return unicode(self.email)



roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))

class Role(db.Model, RoleMixin, LogBase):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __unicode__(self):
        return unicode(self.name)

class User(UserBase, ActiveMixin):
    __tablename__ = 'users'
    address = db.Column(db.String(100))
    zipcode = db.Column(db.String(10))
    city = db.Column(db.String(128))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))




class Manufacturer(db.Model, LogBase):
    __tablename__ = 'manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)

    def __unicode__(self):
        return unicode(self.name)



class Shape(db.Model, LogBase):
    __tablename__ = 'shapes'
    id = db.Column(db.Integer, primary_key=True)
    farmacological_shape = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(256), nullable=True)




class EssentialListCategory(db.Model, LogBase):
    __tablename__ = 'essential_list_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)

    def __unicode__(self):
        return unicode(self.name)







drug_substances = db.Table('drug_substances',
                       db.Column('drug_id', db.Integer, db.ForeignKey('drugs.id')),
                       db.Column('substance_id', db.Integer, db.ForeignKey('substances.id')))

class Regime(db.Model, LogBase):
    __tablename__ = 'regimes'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(128), nullable=False, unique=True)

    def __unicode__(self):
        return unicode(self.description)


class Drug(db.Model, LogBase):
    __tablename__ = 'drugs'
    id = db.Column(db.Integer, primary_key=True)
    protected_name = db.Column(db.String(128), nullable=False, unique=True)

    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'))
    essential_list_id = db.Column(db.Integer, db.ForeignKey('essential_list_categories.id'))
    substance_id = db.Column(db.Integer, db.ForeignKey('substances.id'))
    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    dosage = db.Column(db.String(32))
    instructions = db.Column(db.Text)
    indications = db.Column(db.Text)

    manufacturer = db.relationship('Manufacturer')
    essential_list = db.relationship('EssentialListCategory')
    active_substance = db.relationship('Substance')

    additional_substances = db.relationship('Substance', secondary=drug_substances,
                            backref=db.backref('drugs', lazy='dynamic'))
    regime = db.relationship('Regime')


    def __unicode__(self):
        return unicode(self.protected_name)


class Substance(db.Model, LogBase):
    __tablename__ = 'substances'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)

    def __unicode__(self):
        return unicode(self.name)




class Backlog(db.Model):
    __tablename__ = u"backlogs"
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    obj_type = db.Column(db.String(128), nullable=False)
    operation = db.Column(db.String(32), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), doc='User who made the change', nullable=False)

    data = db.Column(db.TEXT, nullable=False)

    user_email = db.relationship('User')

def versioned_objects(iter):
    for obj in iter:
        if isinstance(obj, LogBase) or isinstance(obj,UserBase):
            yield obj

def create_log(obj,operation):
    from pickle import dumps

    if current_user.is_authenticated():

        #get only table column data, without sqlalchemy control properties
        obj_columns = obj.logme()
        altered_row_id = None
        #save row id if it is integer type
        if "id" in obj_columns:
            altered_row_id = obj_columns['id']

        #pickle object
        data = dumps(obj=obj_columns)

        #current user data
        user = current_user
        user_id = user.id
        ip = user.last_login_ip


        date = datetime.now()
        obj_type = str(type(obj))
        log = Backlog(date=date, operation=operation, data=data, obj_type = obj_type, user_id = user_id, ip_address = ip)
        return log


#save insert/update/delete database events on important tables in Backlog table
@event.listens_for(SessionBase,'before_flush')
def receive_before_flush(session, flush_context,instances):




    for obj in versioned_objects(session.dirty):
        log = create_log(obj, 'update')
        if log:
            session.add(log)

    for obj in versioned_objects(session.deleted):
        log = create_log(obj, 'delete')
        if log:
            session.add(log)

    for obj in versioned_objects(session.new):
        log = create_log(obj, 'insert')
        if log:
            session.add(log)












