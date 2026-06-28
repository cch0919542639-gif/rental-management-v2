from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class ElectricityMeterForm(FlaskForm):
    property_id = SelectField("物件", coerce=int, validators=[DataRequired()])
    room_id = SelectField("房間", coerce=int, validators=[Optional()])
    meter_number = StringField("電表號碼", validators=[Optional()])
    room_number = StringField("房號文字", validators=[Optional()])
    is_main = BooleanField("主電表")
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存電表")


class ElectricityBillForm(FlaskForm):
    property_id = SelectField("物件", coerce=int, validators=[DataRequired()])
    meter_id = SelectField("電表", coerce=int, validators=[Optional()])
    calc_method_id = SelectField("計算方式", coerce=int, validators=[Optional()])
    year_month = StringField("月份 (YYYY-MM)", validators=[DataRequired()])
    period_start = DateField("開始日", validators=[DataRequired()])
    period_end = DateField("結束日", validators=[DataRequired()])
    prev_reading = DecimalField("前次度數", validators=[Optional()], places=1)
    curr_reading = DecimalField("本次度數", validators=[Optional()], places=1)
    total_amount = DecimalField("總電費", validators=[Optional()], places=2)
    public_amount = DecimalField("公電", validators=[Optional()], places=2)
    flow_amount = DecimalField("流動電費", validators=[Optional()], places=2)
    ocr_raw_text = TextAreaField("OCR 原文", validators=[Optional()])
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("建立電費單")


class ElectricityReadingForm(FlaskForm):
    meter_id = SelectField("電表", coerce=int, validators=[DataRequired()])
    room_id = SelectField("房間", coerce=int, validators=[Optional()])
    prev_reading = DecimalField("前次度數", validators=[DataRequired()], places=1)
    curr_reading = DecimalField("本次度數", validators=[DataRequired()], places=1)
    calculated_amount = DecimalField("計算金額", validators=[Optional()], places=2)
    confirmed_amount = DecimalField("確認金額", validators=[Optional()], places=2)
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("新增抄表")


class ElectricityPostForm(FlaskForm):
    monthly_bill_id = IntegerField("月帳單 ID", validators=[DataRequired()])
    reading_id = SelectField("抄表", coerce=int, validators=[DataRequired()])
    public_electricity = DecimalField("回寫公電", validators=[Optional()], places=2)
    submit = SubmitField("回寫月帳單")
