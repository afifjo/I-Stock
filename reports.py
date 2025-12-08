
import io
import pandas as pd
from flask import Blueprint, render_template, make_response, request, send_file, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from models import Item, Staff
from xhtml2pdf import pisa
from datetime import datetime

reports_bp = Blueprint('reports', __name__, template_folder='templates')

def _generate_pdf(html_content):
    """
    Helper to convert HTML content string to PDF bytes.
    """
    result = io.BytesIO()
    # pisaDocument needs bytes or a file-like object usually
    # encoding='UTF-8' helps with special characters
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result)
    
    if not pdf.err:
        result.seek(0)
        return result
    return None

@reports_bp.route('/reports/staff/<int:staff_id>', methods=['GET'])
@login_required
def export_staff(staff_id):
    """
    Export specific staff sheet in PDF or Excel.
    Expects argument ?format=pdf or ?format=excel
    """
    fmt = request.args.get('format', 'pdf')

    staff = Staff.query.get_or_404(staff_id)
    if staff.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.staff_list'))
    
    # Logic to find items assigned to this staff
    # Matches by name string as per the current data model
    items = Item.query.filter(
        Item.user_id == current_user.id,
        Item.assigned_to == staff.name
    ).all()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == 'excel':
        # Create Excel
        # 1. Staff Info
        staff_data = {
            "Name": [staff.name],
            "Email": [staff.email],
            "Phone": [staff.phone],
            "Position": [staff.position],
            "Department": [staff.department]
        }
        
        # 2. Items Info
        items_data = []
        for item in items:
            items_data.append({
                "Item Name": item.name,
                "Category": item.category,
                "Serial Number": item.serial_number,
                "Reference Code": item.reference_code,
                "Quantity": item.quantity,
                "Description": item.description,
                "Assigned Date": item.assigned_date
            })
            
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(staff_data).to_excel(writer, sheet_name='Staff Details', index=False)
            if items_data:
                pd.DataFrame(items_data).to_excel(writer, sheet_name='Assigned Items', index=False)
            else:
                pd.DataFrame({"Info": ["No items assigned"]}).to_excel(writer, sheet_name='Assigned Items', index=False)
                
        output.seek(0)
        return send_file(
            output, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Staff_Report_{staff.name}_{timestamp}.xlsx"
        )
        
    elif fmt == 'pdf':
        # Render HTML template for PDF
        html = render_template('reports/staff_pdf.html', staff=staff, items=items, date=datetime.now())
        pdf_file = _generate_pdf(html)
        
        if pdf_file:
            return send_file(
                pdf_file,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"Staff_Report_{staff.name}_{timestamp}.pdf"
            )
        else:
            flash("Error creating PDF.", "danger")
            return redirect(url_for('main.staff_list'))
            
    else:
        flash("Invalid format selected.", "warning")
        return redirect(url_for('main.staff_list'))


@reports_bp.route('/reports/global', methods=['GET', 'POST'])
@login_required
def global_report():
    """Configurer et exporter un rapport global avec filtres."""

    # Préparer les listes pour le formulaire (catégories, staff) pour GET et POST
    categories = (
        Item.query.with_entities(Item.category)
        .filter(Item.user_id == current_user.id, Item.category.isnot(None))
        .distinct()
        .all()
    )
    categories = [c[0] for c in categories]

    staff_names = (
        Item.query.with_entities(Item.assigned_to)
        .filter(Item.user_id == current_user.id, Item.assigned_to.isnot(None))
        .distinct()
        .all()
    )
    staff_names = [s[0] for s in staff_names]

    if request.method == 'POST':
        # Format de sortie
        fmt = request.form.get('format', 'excel')

        # Filtres
        selected_category = request.form.get('category') or None
        selected_staff = request.form.get('staff') or None
        date_from_str = request.form.get('date_from') or None
        date_to_str = request.form.get('date_to') or None

        date_from = datetime.strptime(date_from_str, '%Y-%m-%d') if date_from_str else None
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d') if date_to_str else None

        # Colonnes choisies
        selected_columns = request.form.getlist('columns')

        if not selected_columns:
            selected_columns = ['name', 'category', 'quantity', 'assigned_to']

        # Noms de colonnes lisibles (français)
        allowed_attrs = {
            'name': "Article",
            'category': 'Catégorie',
            'quantity': 'Quantité',
            'assigned_to': 'Assigné à',
            'serial_number': 'Numéro de série',
            'reference_code': 'Code de référence',
            'description': 'Description',
            'assigned_date': "Date d'affectation",
            'created_at': 'Date de création',
        }

        # Construire la requête avec filtres
        query = Item.query.filter_by(user_id=current_user.id)
        if selected_category:
            query = query.filter(Item.category == selected_category)
        if selected_staff:
            query = query.filter(Item.assigned_to == selected_staff)
        if date_from:
            query = query.filter(Item.created_at >= date_from)
        if date_to:
            # inclure toute la journée de fin
            end_of_day = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Item.created_at <= end_of_day)

        items = query.all()
        
        # Build dataset
        data = []
        for item in items:
            row = {}
            for col in selected_columns:
                if col in allowed_attrs:
                    val = getattr(item, col, None)
                    # format dates
                    if hasattr(val, 'isoformat'):
                        val = val.strftime('%Y-%m-%d')
                    row[allowed_attrs[col]] = val
            data.append(row)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if fmt == 'excel':
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Rapport inventaire', index=False)
            output.seek(0)
            
            return send_file(
                output, 
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"Global_Inventory_{timestamp}.xlsx"
            )

        elif fmt == 'pdf':
            # Tableau HTML puis conversion en PDF
            headers = [allowed_attrs[c] for c in selected_columns if c in allowed_attrs]
            
            html = render_template(
                'reports/global_pdf.html',
                data=data,
                headers=headers,
                date=datetime.now(),
                column_count=len(headers)
            )
            pdf_file = _generate_pdf(html)
            
            if pdf_file:
                return send_file(
                    pdf_file,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f"Global_Inventory_{timestamp}.pdf"
                )
            else:
                flash("Error creating PDF.", "danger")
                return redirect(url_for('reports.global_report'))

    # GET request: Show configuration page
    return render_template(
        'reports/global_report.html',
        categories=categories,
        staff_names=staff_names,
    )
