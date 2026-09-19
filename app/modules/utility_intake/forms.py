from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class UtilityIntakeForm(FlaskForm):
    property_id = SelectField("物件", coerce=int, validators=[DataRequired()])
    utility_type = SelectField("類型", choices=[("electricity", "電費"), ("water", "水費")], validators=[DataRequired()])
    document = FileField(
        "水電單 PDF 或照片",
        validators=[FileRequired(), FileAllowed(["pdf", "png", "jpg", "jpeg", "webp"], "僅接受 PDF 或圖片檔")],
    )
    submit = SubmitField("辨識並建立人工校正草稿")
