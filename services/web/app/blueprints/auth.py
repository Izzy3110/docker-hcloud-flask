import base64
from io import BytesIO
import pyotp
import qrcode
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import current_user, login_user, logout_user, login_required

from services.web.app.extensions.csrf import csrf
from services.web.app.extensions.db import db
from services.web.app.forms import LoginForm, RegisterForm, TwoFactorForm
from services.web.app.models import Users

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/totp_test', methods=['GET', 'POST'])
def totp_test():
    twofactor_form = TwoFactorForm()
    try:
        user_id = current_user.id
        # print(user_id)
        user = db.session.query(Users).filter_by(id=user_id).one_or_none()
        # if user is not None:
        #     print(f"id: {user.id}")
        #     print(f"email: {user.email}")
        #     print(f"username: {user.username}")
        #     print(f"OTP-SECRET: {user.pyotp_secret}")

    except AttributeError as ae:
        user_email = session.get('email')
        # print(f"email: {user_email}")

        user = db.session.query(Users).filter_by(email=user_email).one_or_none()
        # print(request.method)
    if request.method == 'POST':
        # print("is POST")
        # if twofactor_form.validate_on_submit():
        token = twofactor_form.otp.data
        if user.verify_2fa_token(token):
            flash('Logged in successfully.', "success")
            login_user(user, remember=session["remember"])
            return redirect(url_for('general.index'))
        return redirect(url_for("auth.login_2fa_form"))
    if len(user.pyotp_secret) == 0:
       return redirect(url_for('auth.setup_2fa'))

    return render_template("verify-2fa.html", form=twofactor_form)


@auth_bp.route('/login_2fa', methods=['GET', 'POST'])
def login_2fa_form():
    twofactor_form = TwoFactorForm()
    try:
        user_id = current_user.id
        user = db.session.query(Users).filter_by(id=user_id).one_or_none()

    except AttributeError as ae:
        user_email = session.get('email')
        user = db.session.query(Users).filter_by(email=user_email).one_or_none()
    if request.method == 'POST':
        token = twofactor_form.otp.data
        if user.verify_2fa_token(token):
            flash('Logged in successfully.', "success")
            login_user(user, remember=session["remember"])
            return redirect(url_for('general.index'))

        return redirect(url_for("auth.login_2fa_form"))

    if len(user.pyotp_secret) == 0:
        return redirect(url_for('auth.setup_2fa'))

    return render_template("verify-2fa.html", form=twofactor_form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('general.index')), 200

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
                        user_found = True

                    else:
                        flash("User does not exist!", "danger")

                if len(username) > 0:
                    found_user = db.session.query(Users).filter_by(username=username).one_or_none()
                    if found_user is not None:
                        user_found = True

                    else:
                        flash("User does not exist!", "danger")

                if user_found:
                    if found_user.verify_password(password):
                        session["username"] = username
                        session["email"] = email
                        session["remember"] = remember

                        # if current_app.config["2FA_REQUIRED"]:

                        if found_user.user_config_is_two_factor_authentication_enabled:
                            return redirect(url_for("auth.login_2fa_form"))

                        login_user(found_user, remember=remember)

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
                user = Users(email=email, password=password, username=username, two_factor_authentication=False)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("User created!", "success")

                if current_app.config["2FA_REQUIRED"]:
                    return redirect(url_for('auth.setup_2fa'))
                return redirect(url_for('general.index'))
            else:
                flash("User already exists!", "danger")
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)


def generate_2fa_secret():
    return pyotp.random_base32()


def generate_qr_code(username, secret):
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="HCloud Flask")
    img = qrcode.make(totp_uri)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


@auth_bp.route("/show-2fa/<email>")
def show_2fa(email):
    user = db.session.query(Users).filter_by(email=email).one_or_none()
    if user is not None:
        if len(user.pyotp_secret) > 0:
            secret = user.pyotp_secret
            qr = generate_qr_code(email, secret)
            return f'<img src="{qr}"><br>Scan this with Google Authenticator'
        else:
            secret = generate_2fa_secret()
            user.pyotp_secret = secret
            db.session.commit()
            qr = generate_qr_code(email, secret)
            return f'<img src="{qr}"><br>Scan this with Google Authenticator'
    return jsonify({"error": "No User"})


@auth_bp.route("/api/setup-2fa")
def setup_2fa_api():
    if current_user.is_authenticated:
        user = db.session.query(Users).filter_by(id=current_user.id).one_or_none()
        user_email = user.email
        secret = generate_2fa_secret()

        if user is not None:
            qr = generate_qr_code(user_email, secret)
            user.pyotp_secret = secret
            user.two_factor_authentication_setup_required = False
            db.session.commit()

            return qr

        else:
            return jsonify({"system-error": "user not found"})


@csrf.exempt
@auth_bp.route("/api/setup-2fa/verify", methods=['POST'])
@login_required
def setup_2fa_verify_api():

    # print(current_user.id)
    data: dict = request.form.to_dict()
    totp_token = data.get('totp_token', None)
    if totp_token is not None:
        user = db.session.query(Users).filter_by(id=current_user.id).one_or_none()
        if user is not None:
            result = user.verify_2fa_token(totp_token)
            if result:
                user.two_factor_authentication_setup_required = False
                user.user_config_is_two_factor_authentication_enabled = True

            return jsonify({"success": True, "result": result})
    return jsonify({"success": False, "message": "no user"})

@auth_bp.route("/setup-2fa")
def setup_2fa():
    if current_user.is_authenticated:
        user = db.session.query(Users).filter_by(id=current_user.id).one_or_none()
        user_email = user.email
        secret = generate_2fa_secret()

        if user is not None:
            qr = generate_qr_code(user_email, secret)
            user.pyotp_secret = secret
            user.two_factor_authentication_setup_required = False
            db.session.commit()

            return f'<img src="{qr}"><br>Scan this with Google Authenticator'
        else:
            return jsonify({"system-error": "user not found"})

    else:
        user_email = session.get('email')
        user = db.session.query(Users).filter_by(email=user_email).one_or_none()
        if user is not None:
            user_email = user.email
            secret = generate_2fa_secret()
            if request.referrer == "http://127.0.0.1:5005/login":
                qr = generate_qr_code(user_email, secret)
                user.pyotp_secret = secret
                db.session.commit()

                return f'<img src="{qr}"><br>Scan this with Google Authenticator'
            else:
                return jsonify({"error": "ref not allowed"}), 500
        return jsonify({"error": "user not authenticated"}), 401


@auth_bp.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    if request.method == "POST":
        token = request.form["token"]
        username = session.get("username")
        user = db.session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            if user.verify_2fa_token(token):

                return "2FA Verified! Logged in."
        return "Invalid token."
    return '''
        <form method="post">
            2FA Token: <input name="token" />
            <input type="submit" />
        </form>
    '''
