from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class ContractForm(FlaskForm):
    tenant_id = SelectField("房客", coerce=int, validators=[DataRequired()])
    room_id = SelectField("房間", coerce=int, validators=[DataRequired()])
    start_date = DateField("起始日", validators=[DataRequired()])
    end_date = DateField("到期日", validators=[DataRequired()])
    rent = DecimalField("租金", validators=[DataRequired(), NumberRange(min=0)])
    deposit = DecimalField("押金", validators=[Optional(), NumberRange(min=0)])
    electricity_rate = DecimalField("電費費率", validators=[Optional(), NumberRange(min=0)])
    water_rate = DecimalField("水費費率", validators=[Optional(), NumberRange(min=0)])
    start_electricity_reading = DecimalField("起始電表讀數", validators=[Optional()])
    start_water_reading = DecimalField("起始水表讀數", validators=[Optional()])
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存")
