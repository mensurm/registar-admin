__author__ = 'mensur'

from flask import Flask, redirect,url_for
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from registar.models import db
from registar.models import User,Drug, Manufacturer,EssentialListCategory, Role, Substance, Regime, Backlog
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'development_key'
app.config.from_object('config')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#user_datastore.create_user(email='dzukaman@hotmail.com', password='password', firstname='Mujo', lastname='Mujic', real_email='mensur.mandzuka@gmail.com')
#db.session.commit()

@app.route('/')
@login_required
def index():
    return redirect(('/admin'))

class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        return super(MyAdminIndexView, self).index()

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

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyUserView, self).__init__(User, session, **kwargs)


class MyDrugView(MyBaseView):

    #column_list = ('protected_name', 'active_substance')
    # Override displayed fields
    form_columns = ('protected_name', 'manufacturer', 'active_substance', 'additional_substances','dosage','regime','essential_list', 'indications','instructions' )

    column_searchable_list = ('protected_name',)

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyDrugView, self).__init__(Drug, session, **kwargs)


class MyManufacturerView(MyBaseView):

    # Override displayed fields
    column_searchable_list = ('name',)
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyManufacturerView, self).__init__(Manufacturer, session, **kwargs)




class MyEssentialListCategoryView(MyBaseView):

    # Override displayed fields

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyEssentialListCategoryView, self).__init__(EssentialListCategory, session, **kwargs)



class MyRoleView(MyAdminAuthView):
    form_columns = ('name', 'description')
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyRoleView, self).__init__(Role, session, **kwargs)


class MyRegimeView(MyBaseView):
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyRegimeView, self).__init__(Regime, session, **kwargs)



class MySubstanceView(MyBaseView):

    form_columns = ('name', )
    column_searchable_list = ('name',)
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MySubstanceView, self).__init__(Substance, session, **kwargs)


class MyBacklogView(MyAdminAuthView):

    can_create = False

    column_list = ( 'obj_type', 'operation', 'date', 'ip_address', 'user_id','user_email', 'data')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(MyBacklogView, self).__init__(Backlog, session, **kwargs)

class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')



admin = Admin(app,'Registar', index_view=MyAdminIndexView() ,base_template='my_master.html')


admin.add_view(MyDrugView(db.session))
admin.add_view(MySubstanceView(db.session))
admin.add_view(MyManufacturerView(db.session))
admin.add_view(MyRegimeView(db.session))

admin.add_view(MyEssentialListCategoryView(db.session))

admin.add_view(MyUserView(db.session))
admin.add_view(MyRoleView(db.session))
admin.add_view(MyBacklogView(db.session))

admin.add_view(MyView(name='Login'))
