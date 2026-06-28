from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class PaymentCreateForm(FlaskForm):
    contract_id = IntegerField("合約 ID", validators=[Optional()])
    monthly_bill_id = SelectField("帳單", coerce=int, validators=[Optional()])
    amount = DecimalField("付款金額", validators=[DataRequired()], places=2)
    bank_name = StringField("銀行名稱", validators=[Optional()])
    account_number = StringField("帳號後五碼", validators=[Optional()])
    account_holder = StringField("戶名", validators=[Optional()])
    transaction_date = DateField("交易日期", validators=[Optional()])
    payer_name = StringField("付款人", validators=[Optional()])
    transaction_id = StringField("交易編號", validators=[Optional()])
    status_text = StringField("狀態文字", validators=[Optional()])
    ocr_engine = StringField("OCR 引擎", validators=[Optional()])
    image_path = StringField("影像路徑", validators=[Optional()])
    raw_ocr_text = TextAreaField("OCR 原文", validators=[Optional()])
    raw_llm_response = TextAreaField("LLM 回應", validators=[Optional()])
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("建立付款記錄")


class PaymentReviewForm(FlaskForm):
    notes = TextAreaField("審核備註", validators=[Optional()])
    submit = SubmitField("送出")


class PaymentLinkForm(FlaskForm):
    monthly_bill_id = SelectField("目標帳單", coerce=int, validators=[DataRequired()])
    notes = TextAreaField("連結備註", validators=[Optional()])
    submit = SubmitField("連結帳單")
