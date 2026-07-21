from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional


class MoveOutSettlementForm(FlaskForm):
    contract_id = SelectField("合約", coerce=int, validators=[DataRequired()])
    move_out_date = DateField("實際退租日", validators=[DataRequired()])
    final_rent = DecimalField("最後租金", default=0, validators=[InputRequired(), NumberRange(min=0)])
    electricity_amount = DecimalField("電費", default=0, validators=[InputRequired(), NumberRange(min=0)])
    water_amount = DecimalField("水費", default=0, validators=[InputRequired(), NumberRange(min=0)])
    management_fee = DecimalField("管理費", default=0, validators=[InputRequired(), NumberRange(min=0)])
    previous_debt = DecimalField("前期未收", default=0, validators=[InputRequired(), NumberRange(min=0)])
    cleaning_fee = DecimalField("清潔費", default=0, validators=[InputRequired(), NumberRange(min=0)])
    repair_fee = DecimalField("維修費", default=0, validators=[InputRequired(), NumberRange(min=0)])
    other_charge = DecimalField("其他費用", default=0, validators=[InputRequired(), NumberRange(min=0)])
    other_desc = StringField("其他費用說明", validators=[Optional()])
    evidence_type = SelectField("憑證類型（選填）", choices=[("", "未附"), ("cash_signature", "現金簽收"), ("bank_transfer", "轉帳證明"), ("other", "其他")], validators=[Optional()])
    evidence_reference = StringField("憑證參考（選填）", validators=[Optional()])
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存草稿")


class SettlementAllocationForm(FlaskForm):
    final_rent = DecimalField("最後租金分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    electricity_amount = DecimalField("電費分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    water_amount = DecimalField("水費分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    management_fee = DecimalField("管理費分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    previous_debt = DecimalField("前期未收分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    cleaning_fee = DecimalField("清潔費分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    repair_fee = DecimalField("維修費分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    other_charge = DecimalField("其他費用分攤", default=0, validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField("人工確認結算")
