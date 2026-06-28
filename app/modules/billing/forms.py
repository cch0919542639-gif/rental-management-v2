from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class MonthlyBillForm(FlaskForm):
    contract_id = SelectField("合約", coerce=int, validators=[DataRequired()])
    year_month = StringField("月份 (YYYY-MM)", validators=[DataRequired()])
    rent = DecimalField("租金", validators=[DataRequired(), NumberRange(min=0)], places=2)
    electricity_prev = DecimalField("前次電表", validators=[Optional()], places=1)
    electricity_curr = DecimalField("本次電表", validators=[Optional()], places=1)
    electricity_usage = DecimalField("用電量", validators=[Optional()], places=1)
    electricity_amount = DecimalField("電費", validators=[Optional(), NumberRange(min=0)], places=2)
    public_electricity = DecimalField("公電", validators=[Optional(), NumberRange(min=0)], places=2)
    water_prev = DecimalField("前次水表", validators=[Optional()], places=1)
    water_curr = DecimalField("本次水表", validators=[Optional()], places=1)
    water_usage = DecimalField("用水量", validators=[Optional()], places=1)
    water_amount = DecimalField("水費", validators=[Optional(), NumberRange(min=0)], places=2)
    other_charges = DecimalField("其他費用", validators=[Optional(), NumberRange(min=0)], places=2)
    other_desc = StringField("其他費用說明", validators=[Optional()])
    paid = BooleanField("已繳")
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存帳單")


class BillingGenerateForm(FlaskForm):
    year_month = StringField("月份 (YYYY-MM)", validators=[DataRequired()])
    contract_id = IntegerField("合約 ID", validators=[Optional()])
    overwrite_existing = BooleanField("覆蓋既有帳單")
    submit = SubmitField("產生帳單")
