from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from wtforms.validators import Email


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        [DataRequired(), Email(message=("Not a valid email address."))],
        render_kw={"class": "form-control", "autocomplete": "off",},
    )
    password = PasswordField(
        "Password",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )


class RegisterCustomerForm(FlaskForm):
    email = EmailField(
        "Email",
        [DataRequired(), Email(message=("Not a valid email address."))],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    password = PasswordField(
        "Password",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    reconfirm_password = PasswordField(
        "Password",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
