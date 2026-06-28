from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class PropertyForm(FlaskForm):
    landlord_id = SelectField("房東", coerce=int, validators=[DataRequired()])
    name = StringField("名稱", validators=[DataRequired()])
    address = StringField("地址", validators=[Optional()])
    total_rooms = IntegerField("總房數", validators=[Optional(), NumberRange(min=0)])
    electricity_meter_type = SelectField(
        "電表類型",
        choices=[("independent", "獨立電表"), ("shared", "共用電表")],
        validators=[DataRequired()],
    )
    water_meter_type = SelectField(
        "水表類型",
        choices=[("independent", "獨立水表"), ("shared", "共用水表")],
        validators=[DataRequired()],
    )
    billing_rule = StringField("計費規則", validators=[Optional()])
    submit = SubmitField("儲存")
