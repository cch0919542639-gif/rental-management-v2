from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class ReportMonthForm(FlaskForm):
    year_month = StringField("月份 (YYYY-MM)", validators=[DataRequired()])
    submit = SubmitField("查詢")


class ReportYearForm(FlaskForm):
    year = IntegerField(
        "年份",
        validators=[DataRequired(), NumberRange(min=2000, max=2100)],
        default=date.today().year,
    )
    submit = SubmitField("查詢")


class MaintenanceReportForm(FlaskForm):
    property_id = SelectField("物件", coerce=int, choices=[(0, "全部")], validators=[Optional()])
    status = SelectField(
        "狀態",
        choices=[
            ("", "全部"),
            ("reported", "已通報"),
            ("assigned", "已指派"),
            ("in_progress", "處理中"),
            ("resolved", "已解決"),
            ("closed", "已關閉"),
            ("cancelled", "已取消"),
        ],
        validators=[Optional()],
    )
    reported_from = DateField("通報起日", validators=[Optional()])
    reported_to = DateField("通報迄日", validators=[Optional()])
    submit = SubmitField("查詢")
