from edoor.edoor.report.monthly_summary_room_occupy.utils import get_columns,get_filters
import frappe

def get_report(filters):
      
    report_data = get_report_data(filters)
    return {
        "columns":get_report_columns(filters),
        "data": report_data["report_data"],

    }

def get_report_columns(filters):
    report_fields =  get_columns (filters)
    columns = [
        {'key': "Business Source","fieldname":"business_source","label":"Business Source","width":150},
    ]

    for g in report_fields:
        columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })
    
    return columns

def get_report_data(filters):
    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
    calculate_adr_include_all_room_occupied = frappe.db.get_single_value("eDoor Setting", "calculate_adr_include_all_room_occupied")
    report_data =[]
    return  {"report_data":report_data}
   