from wtforms import DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm


class LandlordForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired()])
    phone = StringField("電話", validators=[Optional()])
    electricity_account = StringField("電費戶號", validators=[Optional()])
    water_account = StringField("水費戶號", validators=[Optional()])
    electricity_rate_type = SelectField(
        "電費計價方式",
        choices=[("fixed", "固定單價"), ("floating", "浮動單價")],
        validators=[DataRequired()],
    )
    electricity_rate = DecimalField("電費單價", validators=[Optional()], places=2)
    water_rate_type = SelectField(
        "水費計價方式",
        choices=[("fixed", "固定單價"), ("floating", "浮動單價")],
        validators=[DataRequired()],
    )
    water_rate = DecimalField("水費單價", validators=[Optional()], places=2)
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存")
