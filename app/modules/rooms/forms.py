from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional

from app.services import UtilityPolicyResolver


class RoomForm(FlaskForm):
    property_id = SelectField("房產", coerce=int, validators=[DataRequired()])
    room_number = StringField("房號", validators=[DataRequired()])
    rent = DecimalField("月租金", validators=[Optional(), NumberRange(min=0)])
    deposit = DecimalField("押金", validators=[Optional(), NumberRange(min=0)])
    area_ping = DecimalField("面積（坪）", validators=[Optional(), NumberRange(min=0)])
    status = SelectField("狀態", choices=[("vacant", "空房"), ("occupied", "已出租")], validators=[DataRequired()])
    electricity_policy_code = SelectField(
        "電費策略覆蓋",
        choices=UtilityPolicyResolver.ELECTRICITY_POLICY_CHOICES,
        validators=[Optional()],
    )
    water_policy_code = SelectField(
        "水費策略覆蓋",
        choices=UtilityPolicyResolver.WATER_POLICY_CHOICES,
        validators=[Optional()],
    )
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存")
