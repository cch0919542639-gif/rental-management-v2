from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("帳號", validators=[DataRequired()])
    password = PasswordField("密碼", validators=[DataRequired()])
    submit = SubmitField("登入")
