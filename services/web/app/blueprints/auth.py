from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from services.web.app.extensions.db import db
from services.web.app.forms import LoginForm, RegisterForm
from services.web.app.models import Users

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index')), 200
    if request.method == 'POST':
        if form.validate_on_submit():

            username = form.username.data
            email = form.email.data
            password = form.password.data
            remember = form.remember.data

            # try by email
            if len(email) == 0 and len(username) == 0:
                flash("Error: Username or E-Mail must be defined!", "danger")
            else:
                user_found = False
                found_user = None

                if len(email) > 0:
                    found_user = db.session.query(Users).filter_by(email=email).one_or_none()
                    if found_user is not None:
                        # print("User found!")
                        user_found = True
                    else:
                        flash("User does not exist!", "danger")

                if len(username) > 0:
                    found_user = db.session.query(Users).filter_by(username=username).one_or_none()
                    if found_user is not None:
                        # print("User found!")
                        user_found = True
                    else:
                        flash("User does not exist!", "danger")

                if user_found:
                    # print(found_user.pyotp_secret)
                    # print(password)
                    if found_user.verify_password(password):
                        # flash("Success! Valid Credentials!", "success")
                        login_user(found_user)
                        # two_factor_enabled = True
                        # if two_factor_enabled:
                        #     return redirect(url_for(VERIFY_2FA_URL))

                        flash('Logged in successfully.', "success")
                        login_user(found_user, remember=remember)
                        return redirect(url_for('general.index'))
                    else:
                        flash("Invalid Credentials or User does not exist!", "danger")

            return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You were logged out.", "success")
        return redirect(url_for('general.index'))
    else:
        return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            found_user = db.session.query(Users).filter_by(email=email).one_or_none()
            if found_user is None:
                user = Users(email=email, password=password, username=username)
                db.session.add(user)
                db.session.commit()
                flash("User created!", "success")
            else:
                flash("User already exists!", "danger")
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)
