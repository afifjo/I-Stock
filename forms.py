from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, TextAreaField, SubmitField, SelectField, DecimalField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, Optional
from flask_wtf.file import FileField, FileAllowed

# ---------------------------
# AUTH: LOGIN FORM
# ---------------------------
class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=60)]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=4)]
    )
    submit = SubmitField("Login")


# ---------------------------
# AUTH: REGISTER FORM
# --------------------------- 
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])

    email = StringField("Email", validators=[
        DataRequired(),
        Email(message="Invalid email format.")
    ])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])

    role = SelectField("Account Type", choices=[("user", "User"), ("admin", "Admin")], default="user")
    admin_code = StringField("Admin Code (Required for Admin)", validators=[Optional()])

    submit = SubmitField("Register")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    bio = TextAreaField("Bio", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    location = StringField("Location", validators=[Optional()])
    submit = SubmitField("Save Changes")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class AvatarUploadForm(FlaskForm):
    avatar = FileField("Upload Avatar", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], "Images only!")
    ])
    submit = SubmitField("Upload")

# ---------------------------
# INVENTORY: ADD ITEM FORM
# ---------------------------
class AddItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    quantity = IntegerField("Quantity", default=0, validators=[NumberRange(min=0)])
    
    # Price removed
    
    # New fields
    assigned_to = SelectField("Assigned To (Employee)", choices=[], validators=[Optional()])
    assigned_date = DateField("Assigned Date", format='%Y-%m-%d', validators=[Optional()])

    serial_number = StringField("Serial Number", validators=[Optional(), Length(max=100)])
    reference_code = StringField("Reference Code", validators=[Optional(), Length(max=100)])

    category = SelectField("Category", choices=[
        ("", "— Choose category —"),
        ("mobilier", "🪑 Mobilier & Rangement"),
        ("informatique", "💻 Informatique & Bureautique"),
        ("audiovisuel", "🎥 Audiovisuel"),
        ("electromenager", "☕ Électroménager"),
        ("electricite", "🔌 Électricité, Téléphonie & Divers"),
    ], default="")
    image = FileField("Item Image", validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!")])
    submit = SubmitField("Save Changes")


class StaffForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    position = StringField("Position/Role", validators=[Optional(), Length(max=100)])
    department = StringField("Department", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Save Staff Member")


class EditItemForm(AddItemForm):
    # Inherit fields; templates can change button text
    pass
