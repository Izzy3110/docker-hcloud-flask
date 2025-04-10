from flask_wtf import FlaskForm
from wtforms.fields.simple import EmailField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, InputRequired


class UserProfileForm(FlaskForm):
    two_factor_enabled = BooleanField('Two-Factor enabled')


class TwoFactorForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[
                      InputRequired(), Length(min=6, max=6)])


class RegisterForm(FlaskForm):
    email = EmailField('E-Mail', validators=[DataRequired(), Length(1, 128)])
    username = StringField('Username (optional)')
    password = PasswordField('Password', validators=[DataRequired(), Length(4, 128)])
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = EmailField('E-Mail', validators=[DataRequired(), Length(1, 128)])
    username = StringField('Username (optional)')
    password = PasswordField('Password', validators=[DataRequired(), Length(4, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class PyOTPForm(FlaskForm):
    otp_name = StringField('OTP Name', validators=[DataRequired(), Length(1, 128)])
    otp_secret_key = StringField('OTP Secret', render_kw={"readonly": True})
    submit = SubmitField()
