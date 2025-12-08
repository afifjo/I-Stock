import os
import csv
from io import BytesIO, StringIO
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, abort
from flask_login import login_required, current_user
from extensions import db
from models import Item, Staff, User
from forms import AddItemForm, EditItemForm, StaffForm


bp = Blueprint("main", __name__, template_folder="templates")

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}


# -----------------------------
# FILE VALIDATION
# -----------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def save_image(file_storage):
    """
    Save uploaded image safely.
    """
    if not file_storage:
        return None

    filename = secure_filename(file_storage.filename)
    if not filename or not allowed_file(filename):
        return None

    upload_folder = current_app.config.get(
        "UPLOAD_FOLDER",
        os.path.join(current_app.root_path, "static", "uploads")
    )
    os.makedirs(upload_folder, exist_ok=True)

    basename, ext = os.path.splitext(filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename_final = f"{basename}_{timestamp}{ext}"

    path = os.path.join(upload_folder, filename_final)
    file_storage.save(path)

    return filename_final


# -----------------------------
# HOME PAGE (USER ITEMS ONLY)
# -----------------------------
@bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 6)
    low_stock_threshold = current_app.config.get("LOW_STOCK_THRESHOLD", 5)

    items = Item.query.filter_by(user_id=current_user.id) \
        .order_by(Item.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    # Summary Stats for Dashboard
    total_items = Item.query.filter_by(user_id=current_user.id).count()
    low_stock_count = Item.query.filter(
        Item.user_id == current_user.id,
        Item.quantity < low_stock_threshold
    ).count()

    return render_template(
        "index.html", 
        items=items, 
        low_stock_threshold=low_stock_threshold,
        total_items=total_items,
        low_stock_count=low_stock_count
    )


# -----------------------------
# VIEW ITEM (ONLY IF OWNER)
# -----------------------------
@bp.route("/item/<int:item_id>")
@login_required
def view(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.index"))

    return render_template("view.html", item=item)


# -----------------------------
# ADD ITEM (USER-SPECIFIC)
# -----------------------------
@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = AddItemForm()

    # Populate staff choices
    staff_members = Staff.query.filter_by(user_id=current_user.id).order_by(Staff.name).all()
    form.assigned_to.choices = [("", "— Unassigned —")] + [(s.name, s.name) for s in staff_members]

    if form.validate_on_submit():
        if form.quantity.data > 100000:
            flash("Quantity too large.", "danger")
            return redirect(url_for("main.add"))
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data)

        item = Item(
            name=form.name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            # price removed
            assigned_to=form.assigned_to.data,
            assigned_date=form.assigned_date.data,
            serial_number=form.serial_number.data,
            reference_code=form.reference_code.data,
            category=form.category.data or None,
            image_filename=image_filename,
            user_id=current_user.id  # 🔥 IMPORTANT FIX
        )

        db.session.add(item)
        db.session.commit()

        flash("Item added successfully!", "success")
        return redirect(url_for("main.index"))

    return render_template("add.html", form=form)


# -----------------------------
# EDIT ITEM (ONLY OWNER)
# -----------------------------
@bp.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit(item_id):
    item = Item.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("main.index"))

    form = EditItemForm(obj=item)

    # Populate staff choices
    staff_members = Staff.query.filter_by(user_id=current_user.id).order_by(Staff.name).all()
    form.assigned_to.choices = [("", "— Unassigned —")] + [(s.name, s.name) for s in staff_members]

    if form.validate_on_submit():
        if form.quantity.data > 100000:
            flash("Quantity too large.", "danger")
            return redirect(url_for("main.edit", item_id=item.id))

        # Replace image if new one uploaded
        if form.image.data and form.image.data.filename:
            if item.image_filename:
                old_path = os.path.join(
                    current_app.config.get(
                        "UPLOAD_FOLDER",
                        os.path.join(current_app.root_path, "static", "uploads")
                    ),
                    item.image_filename
                )
                if os.path.exists(old_path):
                    os.remove(old_path)

            item.image_filename = save_image(form.image.data)

        item.name = form.name.data
        item.description = form.description.data
        item.quantity = form.quantity.data
        # price removed
        item.assigned_to = form.assigned_to.data
        item.assigned_date = form.assigned_date.data
        item.serial_number = form.serial_number.data
        item.reference_code = form.reference_code.data
        item.category = form.category.data or None

        db.session.commit()

        flash("Item updated!", "success")
        return redirect(url_for("main.view", item_id=item.id))

    return render_template("edit.html", form=form, item=item)


# -----------------------------
# DELETE ITEM (ONLY OWNER)
# -----------------------------
@bp.route("/delete/<int:item_id>", methods=["POST"])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("main.index"))

    # Delete image file
    if item.image_filename:
        try:
            path = os.path.join(
                current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "static", "uploads")),
                item.image_filename,
            )
            if os.path.exists(path):
                os.remove(path)
        except:
            pass

    db.session.delete(item)
    db.session.commit()

    flash("Item deleted.", "info")
    return redirect(url_for("main.index"))


# -----------------------------
# SEARCH (ONLY USER ITEMS)
# -----------------------------
@bp.route("/search")
@login_required
def search():
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)

    if not q:
        empty = type(
            "obj",
            (object,),
            {"items": [], "has_prev": False, "has_next": False, "page": 1, "pages": 1},
        )()
        return render_template("search.html", items=empty, q=None)

    items = Item.query.filter(
        Item.user_id == current_user.id,
        Item.name.ilike(f"%{q}%")
    ).paginate(page=page, per_page=6, error_out=False)

    return render_template("search.html", items=items, q=q)


# -----------------------------
# DASHBOARD (USER ITEMS ONLY)
# -----------------------------
@bp.route("/dashboard")
@login_required
def dashboard():
    total_items = Item.query.filter_by(user_id=current_user.id).count()

    # Price removed, so total value is not applicable or 0
    total_value = 0

    recent_items = Item.query.filter_by(user_id=current_user.id) \
        .order_by(Item.created_at.desc()) \
        .limit(5).all()

    return render_template(
        "dashboard.html",
        total_items=total_items,
        total_value=total_value,
        recent_items=recent_items
    )


# -----------------------------
# EXPORT CSV (USER ITEMS ONLY)
# -----------------------------
@bp.route("/export/csv")
@login_required
def export_csv():
    items = Item.query.filter_by(user_id=current_user.id).order_by(Item.id).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["id", "name", "description", "quantity", "assigned_to", "assigned_date", "serial_number", "reference_code", "category", "image_filename", "created_at"])

    for it in items:
        writer.writerow([
            it.id,
            it.name,
            it.description or "",
            it.quantity,
            it.assigned_to or "",
            it.assigned_date.isoformat() if it.assigned_date else "",
            it.serial_number or "",
            it.reference_code or "",
            it.category or "",
            it.image_filename or "",
            it.created_at.isoformat(),
        ])

    mem = BytesIO(si.getvalue().encode("utf-8"))
    mem.seek(0)

    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="items_export.csv")


# -----------------------------
# IMPORT CSV (IMPORTS TO USER ONLY)
# -----------------------------
@bp.route("/import/csv", methods=["GET", "POST"])
@login_required
def import_csv():
    if request.method == "POST":
        f = request.files.get("file")
        if not f:
            flash("No file uploaded", "danger")
            return redirect(url_for("main.import_csv"))

        try:
            content = f.stream.read().decode("utf-8")
        except:
            flash("Unable to read file.", "danger")
            return redirect(url_for("main.import_csv"))

        stream = StringIO(content)
        reader = csv.DictReader(stream)
        count = 0

        for row in reader:
            try:
                name = row.get("name") or ""
                if not name:
                    continue
                
                assigned_date_str = row.get("assigned_date", "")
                assigned_date = None
                if assigned_date_str:
                    try:
                        assigned_date = datetime.strptime(assigned_date_str, "%Y-%m-%d").date()
                    except:
                        pass

                item = Item(
                    name=name,
                    description=row.get("description", ""),
                    quantity=int(row.get("quantity", 0)),
                    assigned_to=row.get("assigned_to", ""),
                    assigned_date=assigned_date,
                    serial_number=row.get("serial_number", ""),
                    reference_code=row.get("reference_code", ""),
                    category=row.get("category") or None,
                    user_id=current_user.id   # 👈 import also belongs to user!
                )

                db.session.add(item)
                count += 1
            except:
                continue

        db.session.commit()
        flash(f"Imported {count} items successfully!", "success")
        return redirect(url_for("main.index"))

    return render_template("import_csv.html")


# -----------------------------
# STAFF MANAGEMENT
# -----------------------------

@bp.route("/staff")
@login_required
def staff_list():
    staff_members = Staff.query.filter_by(user_id=current_user.id).order_by(Staff.name).all()
    return render_template("staff_list.html", staff_members=staff_members)


@bp.route("/staff/add", methods=["GET", "POST"])
@login_required
def add_staff():
    form = StaffForm()
    if form.validate_on_submit():
        staff = Staff(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            position=form.position.data,
            department=form.department.data,
            user_id=current_user.id
        )
        db.session.add(staff)
        db.session.commit()
        flash("Staff member added successfully!", "success")
        return redirect(url_for("main.staff_list"))
    return render_template("add_staff.html", form=form, title="Add Staff")


@bp.route("/staff/edit/<int:staff_id>", methods=["GET", "POST"])
@login_required
def edit_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    if staff.user_id != current_user.id:
        abort(403)
    
    form = StaffForm(obj=staff)
    if form.validate_on_submit():
        staff.name = form.name.data
        staff.email = form.email.data
        staff.phone = form.phone.data
        staff.position = form.position.data
        staff.department = form.department.data
        db.session.commit()
        flash("Staff member updated!", "success")
        return redirect(url_for("main.staff_list"))
    
    return render_template("add_staff.html", form=form, title="Edit Staff", is_edit=True)


@bp.route("/staff/delete/<int:staff_id>", methods=["POST"])
@login_required
def delete_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    if staff.user_id != current_user.id:
        abort(403)
    
    db.session.delete(staff)
    db.session.commit()
    flash("Staff member deleted.", "success")
    return redirect(url_for("main.staff_list"))


# -----------------------------
# ADMIN PANEL
# -----------------------------

@bp.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("main.index"))
    
    pending_users = User.query.filter_by(is_approved=False).all()
    approved_users = User.query.filter_by(is_approved=True).all()
    return render_template("admin_users.html", pending_users=pending_users, approved_users=approved_users)


@bp.route("/admin/approve/<int:user_id>", methods=["POST"])
@login_required
def approve_user(user_id):
    if current_user.role != 'admin':
        abort(403)
        
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f"User {user.username} approved!", "success")
    return redirect(url_for("main.admin_users"))


@bp.route("/admin/reject/<int:user_id>", methods=["POST"])
@login_required
def reject_user(user_id):
    if current_user.role != 'admin':
        abort(403)
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} rejected and removed.", "warning")
    return redirect(url_for("main.admin_users"))
