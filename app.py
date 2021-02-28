import flask

from execute import create_dashboard
from flask import send_file, request, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm
import numpy as np
from db import DB
from user import User
import logging.config
import logging
from config import SECRET_KEY, GREETS
import re
from werkzeug.utils import secure_filename
from file_handler import FileHandler
from flask import Flask


class App:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_obj = DB()
        self.db_obj.create_db()
        self.project_name = None
        self.file_handler = None


def create_app():
    try:
        logger = logging.getLogger(__name__)
        logger.info("creates app")
        app = Flask(__name__)
        app.config['SECRET_KEY'] = SECRET_KEY
        app_obj = App()


        @app.route("/")
        @app.route("/home")
        def home():
            app_obj.logger.info("entering the home page")
            return render_template('home.html')

        @app.route('/input_page/<string:email>/<string:user>', methods=['GET'])
        def get_input_project(email, user):
            app_obj.logger.info(
                f"get from the user with the unique email {email} the input data for the app")
            try:
                # name = re.findall("(.*)@", email)[0].capitalize()
                projects = app_obj.db_obj.get_associated_projects(email)
                app_obj.logger.info(f"the projects associated with {user} are: {projects})")
                greets = GREETS
                num = np.random.randint(len(greets))
                return render_template('input_data.html', greeting=greets[num], name=user, email=email,
                                       projects=projects)
            except Exception as err:
                app_obj.logger.error(f"encounter error: {str(err), err.args}")
                flask.make_response(str(err), 500)

        @app.route('/get_file/<string:email>', methods=['GET', 'POST'])
        def set_report_params(email):
            app_obj.logger.info(f"get the report parameters from the user with the unique email {email}")

            try:
                app_obj.logger.info(f"new_project/update an existing project")
                f = request.files['file_name']
                f.save(secure_filename(f.filename))
                app_obj.project_name = re.findall('(.*).csv', f.filename)[0]
                app_obj.logger.info(
                    f"new project / updated data file was loaded. project name {app_obj.project_name}")
                app_obj.db_obj.add_project(email, f.filename)


            except KeyError:
                app_obj.logger.info(f"existing project")
                try:
                    app_obj.project_name = request.form.getlist('project')[0]
                except IndexError:
                    flash("no input was given", 'danger')
                    return redirect(url_for('get_input_project', email=email))

            try:
                df_data = app_obj.db_obj.get_df_from_wiki_data(app_obj.project_name)
                file_handler = FileHandler(df_data)
                app_obj.file_handler = file_handler
                app_obj.file_handler.process_files()
                d_id_title = app_obj.file_handler.d_id_title
                return render_template('report_params.html', d_id_title=d_id_title)
            except Exception as err:
                app_obj.logger.error(f"encounter error: {err.args}")
                flask.make_response(str(err), 500)

        @app.route("/getReport", methods=['GET', 'POST'])
        def execute_app():
            app_obj.logger.info(
                f"creates the report according to the users request for the project "
                f"{app_obj.project_name}")
            try:
                titles = request.form.getlist('title_id')
                app_obj.logger.info(titles)
                if titles is not None and len(titles) > 0:
                    app_obj.logger.info(f"the titles {titles} was chosen")
                    bytes_obj = create_dashboard(app_obj.file_handler, titles)
                else:
                    app_obj.logger.error(f"no title was chosen")
                    app_obj.logger.info("no link was chosen")
                    bytes_obj = create_dashboard(app_obj.file_handler, titles=[])
                    # bytes_obj = create_dashboard()
                return send_file(bytes_obj,
                                 attachment_filename='plot.png',
                                 mimetype='image/png', as_attachment=False, cache_timeout=0)
            except Exception as err:
                app_obj.logger.error(f"encounter error: {err.args}")
                flask.make_response(str(err), 500)

        @app.route("/register", methods=['GET','POST'])
        def register():
            app_obj.logger.info("enter registration page")
            try:
                form = RegistrationForm()
                if form.validate_on_submit():

                    if not app_obj.db_obj.is_record_exist(form.password.data, form.email.data):
                        app_obj.logger.info("adding new user")
                        new_user = User(form.username.data, form.email.data, form.password.data)
                        app_obj.db_obj.add_user(new_user)
                        flash(f'Account created for {form.username.data}!', 'success')
                        return redirect(url_for('home', name=form.username.data))
                    else:
                        flash(f'the user already exists, please log in', 'danger')

                return render_template('register.html', title='Register', form=form)
            except Exception as err:
                app_obj.logger.error(f"encounter error: {err.args}")
                flask.make_response(str(err), 500)

        @app.route("/login", methods=['GET', 'POST'])
        def login():
            app_obj.logger.info("enter login page")
            try:
                form = LoginForm()
                if form.validate_on_submit():
                    password = form.password.data
                    email = form.email.data
                    if app_obj.db_obj.is_record_exist(password, email):
                        app_obj.logger.info("user exists")
                        flash('Login succeed', 'success')
                        db=DB()
                        user_details = db.extract_user_details(password, email)
                        username = user_details.values[0][1]
                        app_obj.logger.info(f"username: {username}")
                        return redirect(url_for('get_input_project', email=email, user=username))
                    else:
                        app_obj.logger.info("user not exists")
                        flash('Login Unsuccessful. Please check username and password', 'danger')
                        return redirect(url_for('login'))
                return render_template('login.html', title='Login', form=form)
            except Exception as err:
                app_obj.logger.error(f"encounter error: {err.args}")
                flask.make_response(str(err), 500)

        @app.route("/info")
        def information():
            app_obj.logger.info("enter info page")
            return render_template('info_page.html')

        @app.route("/page_format")
        def get_data_format():
            app_obj.logger.info("enter the data format page")
            return render_template('data_format.html')

        return app
    except Exception as error:
        logger.info(f"encounter error: {str(error), error.args}")
        flask.make_response(str(error), 500)
