from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class TenantForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired()])
    phone = StringField("電話", validators=[Optional()])
    id_number = StringField("身分證字號", validators=[Optional()])
    emergency_contact = StringField("緊急聯絡人", validators=[Optional()])
    emergency_phone = StringField("緊急聯絡電話", validators=[Optional()])
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存")
