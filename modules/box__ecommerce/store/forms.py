from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField
from wtforms import SubmitField
from wtforms import PasswordField
from wtforms.fields.html5 import EmailField

from wtforms.validators import DataRequired
from shopyoapi.init import idcardphotos
from shopyoapi.init import brnphotos
from shopyoapi.init import addressphotos
from shopyoapi.validators import verify_slug


class StoreRegisterForm(FlaskForm):
    name = StringField(
        "Store Name",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    slug = StringField(
        "Store url e.g. your-store (appears as marketflow.com/store/your-store)",
        [DataRequired(), verify_slug],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    brn = StringField(
        "BRN",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    brn_file = FileField(validators=[FileAllowed(brnphotos, 'Image only!'), FileRequired('File was empty!')])
    location = StringField(
        "Store Location",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    first_name = StringField(
        "First Name",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    last_name = StringField(
        "Last Name",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    email = EmailField(
        "Email",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    password = PasswordField(
        "Password",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    owner_id_card = StringField(
        "ID number",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    owner_id_card_file = FileField(validators=[FileAllowed(idcardphotos, 'Image only!'), FileRequired('File was empty!')])
    owner_address = StringField(
        "Owner Address",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    owner_address_file = FileField(validators=[FileAllowed(addressphotos, 'Image only!'), FileRequired('File was empty!')])
    owner_phone = StringField(
        "Owner Phone",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )


    submit = SubmitField('Register', render_kw={"class": "btn btn-primary", "autocomplete": "off"})
