from datetime import date

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange


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
