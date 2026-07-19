from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError


class PropertyExpenseForm(FlaskForm):
    def validate_amount(self, field):
        if field.data is not None and field.data <= 0:
            raise ValidationError("Expense amount must be positive")

    property_id = SelectField("物件", coerce=int, validators=[DataRequired()])
    transaction_date = DateField("支出日期", validators=[DataRequired()])
    category = SelectField("分類", choices=[("management_fee", "管理費"), ("cleaning", "清潔"), ("repair", "維修"), ("utility", "水電"), ("tax", "稅金"), ("insurance", "保險"), ("supplies", "用品"), ("other", "其他")], validators=[DataRequired()])
    amount = DecimalField("金額", places=2, validators=[DataRequired(), NumberRange(min=0)])
    payee = StringField("收款對象", validators=[Optional()])
    reference_no = StringField("憑證編號", validators=[Optional()])
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存")
