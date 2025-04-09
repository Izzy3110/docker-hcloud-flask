from flask import Blueprint, render_template, current_app, redirect, url_for, request, session
from flask_login import current_user, login_required

from services.web.app.extensions.csrf import csrf
from services.web.app.extensions.db import db
from services.web.app.forms import UserProfileForm
from services.web.app.models import Users

general_bp = Blueprint('general', __name__)


@general_bp.route('/', methods=['GET'])
def index():
    print()
    print(current_app.config["2FA_REQUIRED"] == "True")
    print(current_app.config["2FA_REQUIRED"] == True)
    print(current_app.config["2FA_REQUIRED"])
    print(isinstance(current_app.config["2FA_REQUIRED"], bool))
    print("####")
    return render_template("index.html")

@csrf.exempt
@general_bp.route('/me', methods=['GET', 'POST'])
@login_required
def user_profile():
    form = UserProfileForm()

    user = db.session.query(Users).filter_by(id=current_user.id).one_or_none()
    if not user:
        return redirect(url_for('auth.login'))

    print(user.user_config_is_two_factor_authentication_enabled)
    if request.method == 'POST':
        user.user_config_is_two_factor_authentication_enabled = form.two_factor_enabled.data
        db.session.commit()
        return redirect(url_for("general.user_profile"))

    form.two_factor_enabled.data = user.user_config_is_two_factor_authentication_enabled
    return render_template("user_profile.html", form=form, data={
        "two_factor_authentication_setup_required": user.two_factor_authentication_setup_required,
        "user_config_is_two_factor_authentication_enabled": user.user_config_is_two_factor_authentication_enabled})
