from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class WaterBillForm(FlaskForm):
    property_id = SelectField("物件", coerce=int, validators=[DataRequired()])
    billing_start = DateField("開始日", validators=[DataRequired()])
    billing_end = DateField("結束日", validators=[DataRequired()])
    total_amount = DecimalField("總水費", validators=[DataRequired()], places=2)
    meter_prev_1 = DecimalField("主表前次", validators=[Optional()], places=1)
    meter_curr_1 = DecimalField("主表本次", validators=[Optional()], places=1)
    sub_meter_1 = DecimalField("分表 1", validators=[Optional()], places=1)
    actual_usage_1 = DecimalField("實際用量 1", validators=[Optional()], places=1)
    meter_prev_2 = DecimalField("第二表前次", validators=[Optional()], places=1)
    meter_curr_2 = DecimalField("第二表本次", validators=[Optional()], places=1)
    sub_meter_2 = DecimalField("分表 2", validators=[Optional()], places=1)
    actual_usage_2 = DecimalField("實際用量 2", validators=[Optional()], places=1)
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存水費單")


class WaterPostForm(FlaskForm):
    monthly_bill_id = IntegerField("月帳單 ID", validators=[DataRequired()])
    mode = SelectField(
        "分攤模式",
        choices=[("shared_by_stay_days", "按居住天數分攤"), ("independent_meter", "獨立水表")],
        validators=[DataRequired()],
    )
    amount = DecimalField("獨立水表金額", validators=[Optional()], places=2)
    submit = SubmitField("回寫月帳單")
