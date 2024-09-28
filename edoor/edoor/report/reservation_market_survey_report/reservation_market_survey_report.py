import frappe
meta = frappe.get_meta('Reservation Market Survey') 
def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    totals = calculate_totals(filters)
    data.append(totals)
    summary = summary_totals(filters)
    chart = get_chart(filters)
    return columns, data ,None,chart, summary
def section_fields():
    
    if meta.fields:
        section_breaks = [(field.label, field.idx) for field in meta.fields if field.fieldtype == 'Section Break']
        fields = [(field.fieldname, field.idx) for field in meta.fields if field.fieldtype == 'Check']
        section_to_fields = {}
        for i, (section_label, section_idx) in enumerate(section_breaks):
            next_section_idx = section_breaks[i+1][1] if i+1 < len(section_breaks) else None
            section_to_fields[section_label] = [
                field_name for field_name, field_idx in fields 
                if field_idx > section_idx and (next_section_idx is None or field_idx < next_section_idx)
            ]
    return section_to_fields 
def get_columns(filters):
    view_by = filters.get('view_by')
    columns = [
        {"fieldname": "reservation_name", "label": "Reservation", "fieldtype": "Data", "width": 150},
        {"fieldname": "guest_name", "label": "Guest Name", "fieldtype": "Data", "width": 150}
    ]
    for field in section_fields().get(view_by, []):
        field_meta = meta.get_field(field)
        columns.append({
            "fieldname": field,
            "label": field_meta.label,
            "fieldtype": "Int",
        })

    return columns

def get_chart(filters):
    chart_type = filters.get('chart_type') 
    view_by = filters.get('view_by')
    data = calculate_totals(filters)
    labels = []
    for field in section_fields().get(view_by, []):
        field_meta = meta.get_field(field)
        labels.append(field_meta.label) 
    values = [data[key] for key in data if key != 'reservation_name']
    chart = {'data': {'labels': labels, 'datasets': [{'name':view_by, 'values': values}]}, 
             
             'type': chart_type, 'lineOptions': {'regionFill': 1}, 'valuesOverPoints': 1, 'axisOptions': {'xIsSeries': 1}} 
    return chart
def get_data(filters):
    conditions = []
    filter_values = {}
    if filters.get('property'):
        conditions.append("r.property = %(property)s")
        filter_values['property'] = filters['property']

    # Check for arrival_date filter
    if filters.get('start_arrival_date') and filters.get('end_arrival_date'):
        conditions.append("r.arrival_date BETWEEN %(start_arrival_date)s AND %(end_arrival_date)s")
        filter_values['start_arrival_date'] = filters['start_arrival_date']
        filter_values['end_arrival_date'] = filters['end_arrival_date']
    fields = [field.fieldname for field in meta.fields if field.fieldtype == 'Check']
    col_fields = ',rms.'.join(fields)
    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT r.name AS reservation_name,
               r.guest_name AS guest_name,
               rms.{col_fields}
        FROM `tabReservation` r
        JOIN `tabReservation Market Survey` rms ON r.name = rms.reservation
        {f'WHERE {where_clause}' if where_clause else ''}
    """

    return frappe.db.sql(query, filter_values, as_dict=True)

def summary_totals(filters):
    view_by = filters.get('view_by')
    calculate = calculate_totals(filters)
    output = []
    for field in section_fields().get(view_by, []):
        field_meta = meta.get_field(field)
        output.append({
            "value": calculate[field],
            "indicator": "Green",
            "label": field_meta.label,
            "datatype": "Int"
        })

    return output 

def calculate_totals(filters):
    view_by = filters.get('view_by')
    total_fields = section_fields()
    totals = {field: 0 for field in total_fields.get(view_by, [])}
    totals["reservation_name"] = "Total"
    for row in get_data(filters):
        for field in totals.keys():
            if field != "reservation_name":
                totals[field] += int(row.get(field, 0) or 0)
    return totals
    




