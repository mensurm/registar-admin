# -*- coding: utf-8 -*-
__author__ = 'mensur'

from flask import Flask, redirect,url_for
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import db

from models import User,Drug, Manufacturer,EssentialListCategory, Role, Substance, Regime, Backlog
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required, current_user, logout_user
from flask.ext.security.utils import encrypt_password



from flask_sqlalchemy import SQLAlchemy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'development_key'
app.config.from_object('config')

db.init_app(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#user_datastore.create_user(email='dzukaman@hotmail.com', password='password', firstname='Mujo', lastname='Mujic', real_email='mensur.mandzuka@gmail.com')
#db.session.commit()

@app.teardown_request
def checkin_db(exc):
    try:
        db.close()
    except AttributeError:
        pass

@app.route('/')
#@login_required
def index():
    return redirect(('/admin'))

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return super(MyAdminIndexView,self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))

class MyAdminAuthView(ModelView):
    def is_accessible(self):
        for role in current_user.roles:
            if role.name == 'admin':
                return True
        return False
        #if current_user.is_authenticated():
            #return current_user.roles[0] == 'admin'
        #else:
           #return False


class MyEmployeeAuthView(ModelView):
     def is_accessible(self):
        for role in current_user.roles:
            if role.name == 'pharmacist':
                return True
        return False

class MyAnonymAuthView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated():
            return False
        else:
            return True

class MyLogoutAuthView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated()



class MyBaseView(MyEmployeeAuthView):
    can_create = True
    can_edit = True
    can_delete = True



class MyUserView(MyAdminAuthView):

    # Override displayed fields
    form_columns = ('active','roles', 'email','real_email', 'password', 'firstname', 'lastname', 'phone', 'address', 'city', 'zipcode')
    column_filters = ('email', 'firstname', 'lastname')

    def _on_model_change(self, form, model, is_created):
        if is_created:
            model.password = encrypt_password(model.password)

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyUserView, self).__init__(User, session,name='Korisnici', **kwargs)

class MyDrugAnonymView(MyAnonymAuthView):

    can_create = False
    can_edit = False
    can_delete = False
        #column_list = ('protected_name', 'active_substance')
    # Override displayed fields
    form_columns = ('protected_name', 'manufacturer', 'active_substance', 'additional_substances','dosage','regime','essential_list', 'indications','instructions' )

    #column_searchable_list = ('protected_name', 'dosage', 'instructions')
    column_filters = ('protected_name', 'active_substance', 'manufacturer')
    column_list = ('protected_name', 'active_substance','additional_substances' ,'manufacturer','dosage','regime','indications', 'instructions', 'essential_list' )

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyDrugAnonymView, self).__init__(Drug, session,endpoint='Drugs',name='Spisak lijekova', **kwargs)



class MyDrugView(MyBaseView):

    #column_list = ('protected_name', 'active_substance')
    # Override displayed fields
    form_columns = ('protected_name', 'manufacturer', 'active_substance', 'additional_substances','dosage','regime','essential_list', 'indications','instructions' )

    #column_searchable_list = ('protected_name',)
    column_filters = ('protected_name', 'active_substance', 'manufacturer')
    column_list = ('protected_name', 'active_substance','additional_substances' ,'manufacturer','dosage','regime','indications', 'instructions', 'essential_list' )

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyDrugView, self).__init__(Drug, session,endpoint='Drug',name='Lijekovi', **kwargs)


class MyManufacturerView(MyBaseView):

    # Override displayed fields
    column_searchable_list = ('name',)
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyManufacturerView, self).__init__(Manufacturer, session,name='Proizvođači', **kwargs)




class MyEssentialListCategoryView(MyBaseView):

    # Override displayed fields

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyEssentialListCategoryView, self).__init__(EssentialListCategory, session,name='Esencijalne liste', **kwargs)



class MyRoleView(MyAdminAuthView):
    form_columns = ('name', 'description')
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyRoleView, self).__init__(Role, session,name='Korisničke uloge', **kwargs)


class MyRegimeView(MyBaseView):
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyRegimeView, self).__init__(Regime, session,name='Režimi izdavanja', **kwargs)



class MySubstanceView(MyBaseView):

    form_columns = ('name', )
    column_searchable_list = ('name',)
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MySubstanceView, self).__init__(Substance, session,name='Supstance', **kwargs)


class MyBacklogView(MyAdminAuthView):

    can_create = False
    can_edit = False
    can_delete = False

    column_list = ( 'obj_type', 'operation', 'date', 'ip_address', 'user_id','user_email', 'data')
    column_filters = ('user_email.email','operation', 'obj_type','ip_address')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyBacklogView, self).__init__(Backlog, session,name='Žurnal', **kwargs)
#
# class MyView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('index.html')



admin = Admin(app, 'Registar', index_view=MyAdminIndexView(), base_template='my_master.html')



admin.add_view(MyDrugView(db.session))
admin.add_view(MySubstanceView(db.session))
admin.add_view(MyManufacturerView(db.session))
admin.add_view(MyRegimeView(db.session))

admin.add_view(MyEssentialListCategoryView(db.session))

admin.add_view(MyUserView(db.session))
admin.add_view(MyRoleView(db.session))
admin.add_view(MyBacklogView(db.session))
admin.add_view(MyDrugAnonymView(db.session))

#admin.add_view(MyView(name='Login'))
