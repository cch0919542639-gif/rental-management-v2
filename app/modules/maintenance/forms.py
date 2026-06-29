from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class MaintenanceRequestForm(FlaskForm):
    room_id = SelectField("房間", coerce=int, validators=[DataRequired()])
    issue_category = SelectField(
        "問題分類",
        choices=[
            ("electricity", "電力"),
            ("water", "水務"),
            ("facility", "設備"),
            ("cleaning", "清潔"),
            ("appliance", "家電"),
            ("other", "其他"),
        ],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "優先級",
        choices=[("low", "低"), ("medium", "中"), ("high", "高"), ("urgent", "緊急")],
        validators=[DataRequired()],
    )
    title = StringField("標題", validators=[DataRequired()])
    description = TextAreaField("描述", validators=[Optional()])
    reported_by_name = StringField("通報人", validators=[Optional()])
    assigned_to_name = StringField("指派處理人", validators=[Optional()])
    estimated_cost = DecimalField("預估成本", validators=[Optional()], places=2)
    actual_cost = DecimalField("實際成本", validators=[Optional()], places=2)
    notes = TextAreaField("備註", validators=[Optional()])
    submit = SubmitField("儲存維修單")


class MaintenanceFilterForm(FlaskForm):
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
    priority = SelectField(
        "優先級",
        choices=[("", "全部"), ("low", "低"), ("medium", "中"), ("high", "高"), ("urgent", "緊急")],
        validators=[Optional()],
    )
    room_id = SelectField("房間", coerce=int, validators=[Optional()], choices=[(0, "全部")])
    reported_from = DateField("通報起日", validators=[Optional()])
    reported_to = DateField("通報迄日", validators=[Optional()])
    submit = SubmitField("套用篩選")
