import datetime
from decimal import Decimal

from edoor.api.cache_functions import get_base_rate_cache, get_doctype_tree_name, get_rate_type_info_with_cache
from edoor.api.folio_transaction import create_folio, update_reservation_folio
import frappe
import json
import re
from dateutil.rrule import rrule, MONTHLY
from py_linq import Enumerable
from frappe import local
from frappe.utils.data import getdate,add_to_date
from frappe import _
import calendar
import urllib.parse
import time
import copy
from functools import lru_cache
from edoor.api.update_reservation import update_reservation_stay
from edoor.api.backup import run_backup_command

@frappe.whitelist(allow_guest=True)
def get_theme():
    return frappe.db.get_single_value("ePOS Settings","app_theme")

@frappe.whitelist(allow_guest=True)
def set_port():
    doc = frappe.get_doc("ePOS Settings")
    doc.backend_port="1216"
    doc.save(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist()
def get_room_rate(property, rate_type, room_type, business_source, date):
    sql = "select name from `tabSeason` where '{}' between start_date and end_date limit 1".format(date)
    season = frappe.db.sql (sql, as_dict=1)

    room_type_rate  = frappe.get_value("Room Type", room_type,"rate")
    rate = 0
   
    if season and rate_type:
        season_id = season[0]["name"]
       
        sql = """select 
                    max(rate) as rate 
                from `tabRate Plan` 
                where 
                    property='{}' and
                    season = '{}' and 
                    rate_type = '{}' 
                """.format(property, season_id, rate_type)
     
        if business_source:
            sql_with_business_source = "{} and business_source = '{}'".format(sql, business_source)
            data = frappe.db.sql(sql_with_business_source, as_dict=1)
            rate = data[0]["rate"] or 0
            
            
        if rate ==0:
            #check rate from rate that dont have business source
            sql = "{} and ifnull(business_source,'') = '' ".format(sql) 
            data = frappe.db.sql(sql, as_dict=1)
            rate = data[0]["rate"] or 0

            
    if rate == 0:
        #if still rate = 0 the  get rate from room type
        rate = room_type_rate
    return rate

@frappe.whitelist()
def get_working_day(property = ''):
    working_day = frappe.db.sql("select  posting_date as date,name,pos_profile from `tabWorking Day` where business_branch = %(property)s order by creation desc limit 1",{"property":property},as_dict=1)
    cashier_shift = None
    if len(working_day)>0:
        data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = %(property)s and working_day='{}' and pos_profile='{}' ORDER BY creation desc limit 1".format(working_day[0]["name"],working_day[0]["pos_profile"]),{"property":property},as_dict=1)
        
        if len(data)>0:
            cashier_shift = data[0]
        
    return {
        "date_working_day": working_day[0]["date"] if len(working_day)>0 else '',
        "name":working_day[0]["name"] if len(working_day)>0 else '',
        "cashier_shift":cashier_shift
    }
 
@frappe.whitelist()
def get_chart():
    labels = ["January", "February", "March", "April", "May", "June", "July"]
    values = [10, 20, 30, 40, 50, 60, 70]

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "name": _("Values"),
                "values": values,
                "chartType": "line"
            }
        ]
    }

    chart = frappe.Chart("My Chart", data=chart_data, type="line")
    chart_file_path = frappe.get_app_path("my_custom_app", "public", "charts", "my_chart.png")
    chart.save(chart_file_path)

def successful_login(login_manager):
    pass
 


def update_fetch_from_field(doc, method=None, *args, **kwargs):
    if frappe.db.exists("DocType", "Queue Job"):
        if doc.doctype not in ["Custom HTML Block","Queue Job Configuration","Tag Link","Report","POS User Permission","Custom DocPerm","Translation","User","Audit Trail Document","DocType","File","Sale Product Deleted","POS Print Format Setting","Server Script","Category Note","ePOS Table Position","Scheduled Job Log","Queue Job","POS Account Code Config","Note", "Temp Room Occupy","Contact","DocShare","Doctype","DefaultValue","Print Format","Queue Job","System Console","Scheduled Job Log","Route History","Version","Error Log","Scheduled Job Log","Console Log","Activity Log","Comment"]:
            frappe.get_doc({
                "doctype":"Queue Job",
                "document_name":doc.name,
                "document_type":doc.doctype,
                "action":"update_fetch_from_field"
            }).insert(ignore_permissions=True, ignore_links=True)
        
 

 
def update_keyword(doc, method=None, *args, **kwargs):
    skip_doctypes = ["Folio Transaction","City Ledger","Vendor","Customer","Reservation Stay","Reservation","Reservation Stay Room","Room","Room Block","Business Source"]
    if  doc.doctype in skip_doctypes:
        frappe.get_doc({
            "doctype":"Queue Job",
            "document_name":doc.name,
            "document_type":doc.doctype,
            "action":"update_keyword"

        }).insert(ignore_permissions=True, ignore_links=True)

        # frappe.enqueue("edoor.api.utils.update_keyword_queue", queue='long', doc=doc)

    
    




def update_comment_after_insert(doc, method=None, *args, **kwargs):
    if doc.comment_type=="Deleted":
        return
    if doc.comment_type == "Workflow": return
   
    #if doc have property field then update property, audit_date and is audit trail to true
    update_files = ["comment_by='{}'".format(frappe.db.get_value("User",doc.owner, "full_name"))]
    update_files.append("custom_comment_by_photo='{}'".format(frappe.db.get_value("User",doc.owner, "user_image") or ""))
    updated_data = {}
    if not doc.custom_icon:
        icon_data = frappe.db.sql("select icon from `tabApp Icons` where name='{}'".format(doc.custom_audit_trail_type), as_dict=1)
        icon = 'pi pi-stop'
        if icon_data:
            icon = icon_data[0]["icon"]

        update_files.append("custom_icon='{}'".format(icon))
    
    if doc.reference_name:
        ref_doc = frappe.get_doc(doc.reference_doctype,doc.reference_name )
        if doc.reference_name and not doc.custom_property:
            if hasattr(ref_doc, "property"):
                working_day = get_working_day(ref_doc.property)
                update_files.append("custom_property=%(property)s")
                updated_data["property"] = ref_doc.property
                update_files.append("custom_posting_date='{}'".format(working_day["date_working_day"] or frappe.utils.now()))
                update_files.append("custom_is_audit_trail=1")
                
                if doc.comment_type=="Attachment":
                    
                    link = doc.content
                    file_name = re.search(r'<a href="([^"]+)"', link).group(1) # extract the text between the quotes
                    file_name = file_name.split('/')[-1] # get the last part 
                    file_name = urllib.parse.unquote(file_name)
                    

                    file_data = frappe.db.get_list("File", filters={"file_url":"/files/" + file_name})

                    if len(file_data)>0:
                        file_doc = frappe.get_doc("File", file_data[0]["name"])
                        if file_doc.custom_show_in_edoor==0:
                            update_files.append("custom_is_audit_trail=0")
        else:
            if not doc.custom_cashier_shift:
                working_day = get_working_day( doc.custom_property)
                update_files.append("custom_cashier_shift='{}'".format("" if not working_day["cashier_shift"] else working_day["cashier_shift"]["name"]))
                

        # get field for relate document for easy get data in report
        
        if hasattr(ref_doc,"reservation"):
            update_files.append("custom_reservation='{}'".format(ref_doc.reservation or ""))
        if hasattr(ref_doc,"reservation_stay"):
            update_files.append("custom_reservation_stay='{}'".format(ref_doc.reservation_stay or ""))
        
        if hasattr(ref_doc,"transaction_type"):
            update_files.append("custom_folio_transaction_type='{}'".format(ref_doc.transaction_type or ""))
            update_files.append("custom_folio_number='{}'".format(ref_doc.transaction_number or ""))
    
        if hasattr(ref_doc,"guest"):
            update_files.append("custom_guest='{}'".format(ref_doc.guest or ""))

    


    #update custom field base on reference document type
    #custom_reservation
    if doc.reference_doctype == "Reservation" and not doc.custom_reservation:
        update_files.append("custom_reservation='{}'".format(doc.reference_name))
    #custom_reservation_stay
    if doc.reference_doctype == "Reservation Stay" and not doc.custom_reservation_stay:
        update_files.append("custom_reservation_stay='{}'".format(doc.reference_name))
    
    #custom_guest
    if doc.reference_doctype == "Customer" and not doc.custom_guest:
        update_files.append("custom_guest='{}'".format(doc.reference_name))
    
    #custom_folio_transaction
    if doc.reference_doctype == "Folio Transaction" and not doc.custom_folio_transaction:
        update_files.append("custom_folio_transaction='{}'".format(doc.reference_name))
    
    #custom_room_block
    if doc.reference_doctype == "Room Block" and not doc.custom_room_block:
        update_files.append("custom_room_block='{}'".format(doc.reference_name))
    
    #custom transaction type and custom folio number
    if doc.reference_doctype in ['Deposit Ledger','Desk Folio','Payable Ledger', 'Reservation Folio', 'City Ledger', 'Cashier Shift'] and not doc.custom_folio_transaction_type:
        update_files.append("custom_folio_transaction_type='{}'".format(doc.reference_doctype))
        update_files.append("custom_folio_number='{}'".format(doc.reference_name))

    
    
    

    if not doc.subject:
        if doc.comment_type=="Attachment Removed":
            update_files.append("subject='Removed Attachment'".format(doc.comment_type))
        else:
            if not  doc.subject:
                update_files.append("subject='Adding {}'".format(doc.comment_type))

    
   
    frappe.db.sql("update `tabComment` set {} where name='{}'".format(",".join(update_files), doc.name),updated_data)
 
    frappe.db.commit()

def update_comment_keyword(doc, method=None, *args, **kwargs):
    if doc.custom_is_audit_trail==1:
        frappe.db.sql("update `tabComment` set custom_keyword=concat(ifnull(subject,''), ' ', ifnull(content,''), ' ', ifnull(reference_name,''),' ',ifnull(custom_item_description,''), ' ', ifnull(custom_note,'')  ) where name='{}'".format(doc.name))
        frappe.db.commit()


def update_audit_trail_from_version(doc, method=None, *args, **kwargs):
    
    if frappe.db.exists("Audit Trail Document",doc.ref_doctype,cache=True):
        submit_update_audit_trail_from_version(doc)
        # frappe.enqueue("edoor.api.utils.submit_update_audit_trail_from_version", queue='short', doc=doc)

def submit_update_audit_trail_from_version(doc):
    if frappe.db.exists("Audit Trail Document",doc.ref_doctype,cache=True):
        doctype = frappe.get_doc("Audit Trail Document", doc.ref_doctype)
        data = json.loads(doc.data)
        data_changed = []
        if doc.ref_doctype == "Reservation Room Rate":
            data_changed.append("<b>Date:</b> " +  frappe.db.get_value("Reservation Room Rate", doc.docname,"date").strftime('%d-%m-%Y'))

        for d in data["changed"]:
            if d[0] in [f.field_name for f in doctype.tracking_field] and ((d[1] or '')!='' or (d[2] or '')!=''):
                field = [f  for f in doctype.tracking_field if f.field_name==d[0]][0]
                if field.field_type=="Check":
                    data_changed.append(f'<b>{field.label}</b>: {"Yes" if d[1]==1 else "No"} <b>to</b> {"Yes" if d[2]==1 else "No"}')
                elif 'tax_' in field.field_name:
                    ref_doc = frappe.get_doc(doc.ref_doctype,doc.docname)
                    if field.field_name == 'tax_1_rate':
                        data_changed.append(f'<b>{ref_doc.tax_1_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    elif field.field_name == 'tax_1_amount':
                        data_changed.append(f'<b>{ref_doc.tax_1_name} Amount </b>: {d[1]} <b>to</b> {d[2]}')
                    elif field.field_name == 'tax_2_rate':
                        data_changed.append(f'<b>{ref_doc.tax_2_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    elif field.field_name == 'tax_2_amount':
                        data_changed.append(f'<b>{ref_doc.tax_2_name} Amount </b>: {d[1]} <b>to</b> {d[2]}')
                    elif field.field_name == 'tax_2_rate':
                        data_changed.append(f'<b>{ref_doc.tax_2_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    
                    elif field.field_name == 'tax_3_rate':
                        data_changed.append(f'<b>{ref_doc.tax_3_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    elif field.field_name == 'tax_3_amount':
                        data_changed.append(f'<b>{ref_doc.tax_3_name} Amount </b>: {d[1]} <b>to</b> {d[2]}')
                        
                else:
                    if field.hide_old_value==1:
                        data_changed.append(f'<b>{field.label}</b>: {d[2]}')
                    else:
                        data_changed.append(f'<b>{field.label}</b>: {d[1]} <b>to</b> {d[2]}')


        if doc.ref_doctype == "Reservation Room Rate":
            if len(data_changed)==1:
                #we skip it cause have only 1 record is date
                return

        if len(data_changed)>0:
            comment_doc = []
            comment_doc.append({
            "creation":doc.creation,
            "subject": "Change Value",
            "custom_audit_trail_type":"Updated",
            "custom_icon":"pi pi-file-edit",
            "reference_doctype":doc.ref_doctype,
            "reference_name":doc.docname,
            "content":", ".join(data_changed)  
            })
            # frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)
            add_audit_trail(comment_doc, update_creation_date=True)


    



def check_field(doc, key):
    if key in doc.keys():
        if  doc[key].strip():
            return True
    return False 

@lru_cache(maxsize=128)
def get_date_range(start_date, end_date, exlude_last_date=True):
 
    # Create an empty list to store the generated dates.
    dates = []
    for i in range((end_date - start_date).days + 1):
        
        if start_date + datetime.timedelta(days=i) == end_date:
            if not exlude_last_date:
                dates.append(start_date + datetime.timedelta(days=i))    
        else:
            dates.append(start_date + datetime.timedelta(days=i))

    # Return the generated dates.
    return dates

@frappe.whitelist()
def update_reservation(name=None,doc=None, run_commit = True,ignore_validate=False):
    if name or doc:
        if name:
            if not frappe.db.exists("Reservation", name):
                return
            doc = frappe.get_doc("Reservation",name)

        sql = """select 
                    min(if(is_active_reservation=0,'2050-01-01', arrival_date)) as arrival_date,
                    max(if(is_active_reservation=0,'2000-01-01', departure_date)) as departure_date,
                    count(name) as total_stay,
                    sum(if(is_active_reservation =1,1,0)) as total_active_stay, 
                    sum(if(is_active_reservation =1,adult,0)) as adult, 
                    sum(if(is_active_reservation =1,child,0)) as child ,
                    
                    sum(if(is_active_reservation=1 and reservation_status='Reserved',1,0)) as total_reserved,
                    sum(if(is_active_reservation=1 and reservation_status='Confirmed',1,0)) as total_confirmed,
                    sum(if(is_active_reservation=1 and reservation_status='In-house',1,0)) as total_checked_in,
                    sum(if(is_active_reservation=1 and reservation_status='Checked Out',1,0)) as total_checked_out,
                    sum(if(is_active_reservation=0 and reservation_status='Cancelled',1,0)) as total_cancelled,
                    sum(if(is_active_reservation=0 and reservation_status='No Show',1,0)) as total_no_show,
                    sum(if(is_active_reservation=0 and reservation_status='Void',1,0)) as total_void,
                    
                    sum(if(is_active_reservation =1,total_amount,0)) as total_amount,
                    sum(if(is_active_reservation =1,room_nights,0)) as room_nights,
                    sum(if(is_active_reservation=1,total_tax,0)) as total_tax,
                    sum(if(is_active_reservation=1,total_discount,0)) as total_discount,
                    max(is_complimentary) as is_complimentary, 
                    max(is_house_use) as is_house_use
                from `tabReservation Stay`
                where 
                    reservation='{}'
                """.format(name)
        
        data = frappe.db.sql(sql,as_dict=1)
 
        #get folio summary
        sql_folio = """
            select  
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                reservation = '{}' and 
                transaction_type = 'Reservation Folio'
        """.format(
            doc.name
        )

        folio_data = frappe.db.sql(sql_folio, as_dict=1)
        
        #get room_numbers, room_type , and room_type alias
        sql_room_info = """
                    SELECT 
                        GROUP_CONCAT(rooms) as rooms,
                        GROUP_CONCAT(room_types) as room_types,
                        GROUP_CONCAT(room_type_alias) as room_type_alias,
                        GROUP_CONCAT(name) as room_stay 
                        FROM `tabReservation Stay`
                    where 
                        is_active_reservation = 1 and 
                        reservation = '{}'
        """.format(doc.name)
        room_info_data =frappe.db.sql(sql_room_info, as_dict=1)

 

        doc.total_debit = folio_data[0]["debit"] or 0
        doc.total_credit= folio_data[0]["credit"] or 0
        doc.balance = doc.total_debit - doc.total_credit

        currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
        if abs(round(doc.balance, int(currency_precision)))<= (Decimal('0.1') ** int(currency_precision)):
            doc.balance = 0
        

        #update to reservation
        #get min and max active stay
        stay_date  =frappe.db.sql( "select min(arrival_date) as arrival_date, max(departure_date) as departure_date from `tabReservation Stay` where reservation='{}' and is_active_reservation=1".format(doc.name),as_dict=1)
        doc.arrival_date = stay_date[0]["arrival_date"]  or doc.arrival_date
        doc.departure_date= stay_date[0]["departure_date"] or   doc.departure_date

        
        doc.adult = data[0][ "adult"]
        doc.child = data[0][ "child"]

        doc.room_nights= data[0]["room_nights"]
        doc.total_amount= data[0]["total_amount"]
        # doc.room_rate= data[0]["room_rate"]
        if (data[0]["room_nights"] or 0)>0:
            doc.adr= data[0]["total_amount"] / data[0]["room_nights"]
        else:
            doc.adr = 0
        doc.total_discount= data[0]["total_discount"]
        doc.total_tax= data[0]["total_tax"]
        
        doc.total_reservation_stay = data[0][ "total_stay"]
        doc.total_active_reservation_stay = data[0][ "total_active_stay"]

        doc.reserved= data[0]["total_reserved"] or 0
        doc.total_confirmed= data[0]["total_confirmed"] or 0
        doc.total_checked_in= data[0]["total_checked_in"] or 0
        doc.total_checked_out= data[0]["total_checked_out"] or 0
        doc.total_cancelled= data[0]["total_cancelled"] or 0
        doc.total_void= data[0]["total_void"] or 0
        doc.total_no_show= data[0]["total_no_show"] or 0
        doc.is_complimentary= data[0]["is_complimentary"] or 0
        doc.is_house_use= data[0]["is_house_use"] or 0
        
        #update room info
        
        doc.room_types ="" if not room_info_data[0]["room_types"] else  ",".join(set(room_info_data[0]["room_types"].split(',')))
        doc.room_numbers ="" if not room_info_data[0]["rooms"] else  ",".join(set(d for d in  room_info_data[0]["rooms"].split(',') if d !=''))
        doc.room_type_alias ="" if not room_info_data[0]["room_type_alias"] else ",".join(set(room_info_data[0]["room_type_alias"].split(','))) 
        # update room info json
        room_stays_list = []
        room_stay_data = []
        if room_info_data[0]["room_stay"]:
            room_stays_list = room_info_data[0]["room_stay"].split(",")
            room_stays = ','.join(f"'{x}'" for x in room_stays_list)
            sql_room_json = "SELECT `name`, room_number, room_type, room_type_alias,parent as reservation_stay FROM `tabReservation Stay Room` WHERE parent IN({})".format(room_stays)
            room_stay_data = frappe.db.sql(sql_room_json, as_dict=1)

        room_stay_json_list = []
        if len(room_stay_data) > 0:
            for s in room_stay_data:
                room_stay_json_list.append({
                    "name": s['name'],
                    "room_number": s['room_number'] or '',
                    "room_type_alias": s['room_type_alias'],
                    "room_type": s['room_type'],
                    "reservation_stay": s['reservation_stay']
                })
        doc.rooms_data = json.dumps(room_stay_json_list)
    
        #update reservation status
      
        if (doc.total_confirmed or 0) >0:
            doc.reservation_status = 'Confirmed'
        elif (doc.reserved or 0)>0:
            doc.reservation_status = 'Reserved'
        elif (doc.total_checked_in or 0)>0 and  (doc.reserved or 0)==0:
            doc.reservation_status = 'In-house'
        elif  (doc.reserved or 0)== 0 and (doc.total_checked_in or 0)==0 and (doc.total_checked_out or 0) > 0:
            doc.reservation_status = 'Checked Out'
        elif (doc.total_no_show+ doc.total_cancelled + doc.total_void > 0 ) and doc.total_active_reservation_stay == 0:
            if doc.total_no_show > 0:
                doc.reservation_status = 'No Show'
            elif doc.total_cancelled > 0:
                doc.reservation_status = 'Cancelled'
            else:
                doc.reservation_status = "Void" 

        doc.flags.ignore_on_update= True
        doc.flags.ignore_validate = ignore_validate
        doc.save(ignore_permissions=True)
        if run_commit:
            frappe.db.commit()
        return doc



@frappe.whitelist()
def update_deposit_ledger(name=None, doc=None,run_commit=True,ignore_validate=False, ignore_on_update=False):

    if name:
        doc = frappe.get_doc("Deposit Ledger",name)
    sql_folio = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'Deposit Ledger' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql_folio, as_dict=1)


    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.balance= (doc.total_debit or 0) - (doc.total_credit or 0)
    doc.flags.ignore_validate = ignore_validate
    doc.flags.ignore_on_update = ignore_on_update
    doc.save(ignore_permissions=True)
    
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_desk_folio(name=None, doc=None,run_commit=True,ignore_validation = False, ignore_on_update=False):

    if name:
        doc = frappe.get_doc("Desk Folio",name)
    sql_folio = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'Desk Folio' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql_folio, as_dict=1)


    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.flags.ignore_validate = ignore_validation
    doc.flags.ignore_on_update = ignore_on_update
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_payable_ledger(name=None, doc=None,run_commit=True,ignore_validate = False, ignore_on_update=False):

    if name:
        doc = frappe.get_doc("Payable Ledger",name)
    sql_folio = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'Payable Ledger' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql_folio, as_dict=1)


    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.flags.ignore_validate = ignore_validate
    doc.flags.ignore_on_update = ignore_on_update
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_city_ledger(name=None,doc=None, run_commit = True,ignore_validate = False, ignore_on_update=False):
    if name:
        doc = frappe.get_doc("City Ledger",name)
    sql = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'City Ledger' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql, as_dict=1)

    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.balance= (doc.total_debit or 0) - (doc.total_credit or 0)
    doc.flags.ignore_validate = ignore_validate
    doc.flags.ignore_on_update = ignore_on_update
    doc.save( ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc




@frappe.whitelist()
def get_base_rate(amount,tax_rule,tax_1_rate, tax_2_rate,tax_3_rate):
    return get_base_rate_cache(amount,tax_rule,tax_1_rate, tax_2_rate,tax_3_rate)


@frappe.whitelist(methods="DELETE")
def delete_doc(doctype, name, note):
    doc = frappe.get_doc(doctype,name)
    if hasattr(doc,"deleted_note"):
        frappe.db.sql("update `tab{}` set deleted_note = '{}' where name='{}'".format(doctype,note or "",name))
    frappe.delete_doc(doctype,name)

@frappe.whitelist()
def remove_temp_room_occupy(reservation):
    frappe.db.sql(""" 
                    delete from `tabTemp Room Occupy` 
                    where  
                        reservation_stay in (
                                select 
                                    name 
                                from `tabReservation Stay` 
                                where reservation = '{0}' and 
                                (is_active_reservation = 0 or reservation_status ='Checked Out') 
                        ) and 
                        reservation = '{0}'
                  """.format(reservation))
    frappe.db.commit()

def add_room_charge_to_folio(folio,rate,is_package=0,is_night_audit_posing=0,note="",working_day=None, cashier_shift=None,ignore_validateion_cashier_shift=False, ignore_validate_back_date_transaction=False,ignore_update_folio_transaction=False,ignore_update_reservation_folio=False ):
    rate_type_doc = frappe.get_doc("Rate Type", rate.rate_type)
    data = frappe.db.sql("select name from  `tabFolio Transaction` where reservation_room_rate='{}' and account_code='{}'".format(rate.name,rate_type_doc.account_code),as_dict=1)
    if not data :
        doc = {
            "doctype":"Folio Transaction",
            "transaction_type":"Reservation Folio",
            "working_day":working_day,
            "cashier_shift":cashier_shift,
            "posting_date":rate.date,
            "transaction_number":folio.name,
            "room_type_id":rate.room_type_id,
            "room_id":rate.room_id,
            "input_amount":rate.input_rate,
            "account_code":rate_type_doc.account_code,
            "tax_rule":rate.tax_rule,
            "discount_type":rate.discount_type,
            "discount":rate.discount,
            "tax_1_rate":rate.tax_1_rate,
            "tax_2_rate":rate.tax_2_rate,
            "tax_3_rate":rate.tax_3_rate,
            "rate_include_tax":rate.rate_include_tax,
            "is_auto_post":1,
            "reservation_room_rate": rate.name,
            "source_reservation_stay": rate.reservation_stay,
            "stay_room_id": rate.stay_room_id,
            "is_night_audit_posing":is_night_audit_posing,
            "note":note,
            "is_package":is_package,
            "adult": rate.adult or 1,
            "child":rate.child or 0
        }
        
        doc = frappe.get_doc(doc)
        doc.flags.valiate_input_amount = False
        doc.flags.ignore_update_reservation = True
        doc.flags.ignore_validate_close_folio = True
        doc.flags.ignore_validateion_cashier_shift = ignore_validateion_cashier_shift
        doc.flags.ignore_validate_back_date_transaction = ignore_validate_back_date_transaction
        doc.flags.ignore_update_folio_transaction = ignore_update_folio_transaction
        doc.flags.ignore_update_reservation_folio = ignore_update_reservation_folio
        doc.flags.is_auto_post = True
        
        doc.insert()
        return doc
    
    return None

def add_package_inclusion_charge_to_folio(folio,rate,is_night_audit_posing=0,note="",working_day=None, cashier_shift=None,ignore_validateion_cashier_shift=False, ignore_validate_back_date_transaction=False,ignore_update_folio_transaction=False,ignore_update_reservation_folio =False):
    doc = {
        "doctype":"Folio Transaction",
        "transaction_type":"Reservation Folio",
        "naming_series":rate["reference_folio_transaction"] + ".-.##",
        "working_day":working_day,
        "cashier_shift":cashier_shift,
        "posting_date":rate["date"],
        "transaction_number":folio.name,
        "room_type_id":rate["room_type_id"],
        "room_id":rate["room_id"],
        "input_amount":rate["input_rate"],
        "account_code":rate["account_code"],
        "tax_rule":rate["tax_rule"],
        "discount_type":rate["discount_type"],
        "discount":rate["discount"],
        "tax_1_rate":rate["tax_1_rate"],
        "tax_2_rate":rate["tax_2_rate"],
        "tax_3_rate":rate["tax_3_rate"],
        "rate_include_tax":rate["rate_include_tax"],
        "is_auto_post":1,
        "reservation_room_rate": rate["name"],
        "source_reservation_stay": rate["reservation_stay"],
        "stay_room_id": rate["stay_room_id"],
        "is_night_audit_posing":is_night_audit_posing,
        "note":note,
        "is_package_inclusion_item":1,
        "reference_folio_transaction":rate["reference_folio_transaction"],
        "parent_reference":rate["parent_reference"],
        "is_sub_package_charge":1,
        "adult":rate["adult"],
        "child":rate["child"],
        "quantity":0 if not "quantity" in rate else rate["quantity"],
        "report_quantity":0 if not "quantity" in rate else rate["quantity"]
        
    }
    
    doc = frappe.get_doc(doc)
    doc.flags.valiate_input_amount = False
    doc.flags.ignore_update_reservation = True
    doc.flags.ignore_validate_close_folio = True
    doc.flags.ignore_validateion_cashier_shift = ignore_validateion_cashier_shift
    doc.flags.ignore_validate_back_date_transaction = ignore_validate_back_date_transaction
    doc.flags.ignore_update_folio_transaction = ignore_update_folio_transaction
    doc.flags.ignore_update_reservation_folio = ignore_update_reservation_folio
    doc.flags.is_auto_post = True


    doc.insert()
    return doc


@frappe.whitelist()
def clear_reservation():
    
    if  frappe.session.user =="Administrator":
        pass
        # run_backup_command()
        # frappe.db.sql("delete from `tabReservation`")
        # frappe.db.sql("delete from `tabReservation Stay`")
        # frappe.db.sql("delete from `tabReservation Stay Room`")
        # frappe.db.sql("delete from `tabReservation Room Rate`")
        # frappe.db.sql("delete from `tabTemp Room Occupy`")
        # frappe.db.sql("delete from `tabRoom Occupy`")
        # frappe.db.sql("delete from `tabFolio Transaction`")
        # frappe.db.sql("delete from `tabReservation Folio`")
        # frappe.db.sql("update `tabRoom` set housekeeping_status = 'Vacant Clean', reservation_stay='',guest='' , guest_name=''")
        
        # frappe.db.sql("delete from `tabSale Product`")
        # frappe.db.sql("delete from `tabSale Payment`")
        # frappe.db.sql("delete from `tabSale`")
        # frappe.db.sql("delete from `tabWorking Day`")
        # frappe.db.sql("delete from `tabCashier Shift`")
        # frappe.db.sql("delete from `tabRoom Block`")
        # frappe.db.sql("delete from `tabDeposit Ledger`")
        # frappe.db.sql("delete from `tabDesk Folio`")
        # frappe.db.sql("delete from `tabCashier Shift Cash Count`")
        # frappe.db.sql("delete from `tabDaily Property Data`")
        # frappe.db.sql("delete from `tabAdditional Stay Guest`")
        # frappe.db.sql("delete from `tabReservation Stay Package Items`")
        # frappe.db.sql("delete from `tabRevenue Forecast Breakdown`")
        # frappe.db.sql("delete from `tabTax Invoice`")

        # frappe.db.sql("delete from `tabComment` where reference_doctype in  ('Reservation','Reservation Stay','Reservation Stay Room','Reservation Room Rate','Temp Room Occupy','Room Occupy','Folio Transaction','Reservation Folio','Sale Product','Sale Payment','Sale','Working Day','Cashier Shift','Frontdesk Note','Room Block')")
        # frappe.db.sql("delete from `tabComment` where custom_is_note=1")

        # frappe.db.sql("delete from `tabFile` where attached_to_doctype in  ('Reservation','Reservation Stay','Reservation Stay Room','Reservation Room Rate','Temp Room Occupy','Room Occupy','Folio Transaction','Reservation Folio','Sale Product','Sale Payment','Sale','Working Day','Cashier Shift','Frontdesk Note','Room Block')")
        # frappe.db.sql("delete from `tabVersion` where ref_doctype in  ('Reservation','Reservation Stay','Reservation Stay Room','Reservation Room Rate','Temp Room Occupy','Room Occupy','Folio Transaction','Reservation Folio','Sale Product','Sale Payment','Sale','Working Day','Cashier Shift','Frontdesk Note','Room Block')")

        # frappe.db.sql("update `tabCity Ledger` set total_debit = 0, total_credit=0, balance=0")
        




        # room_list = frappe.db.get_all("Room")

        # for r in room_list:

        #     room_doc = frappe.get_doc("Room", r.name)
        #     room_doc.room_status = "Vacant"
        #     room_doc.housekeeping_status_code = "Clean"
            
        #     room_doc.save()
        
        # business_branch = frappe.get_last_doc('Business Branch') 
        # frappe.get_doc({
        #     "posting_date":frappe.utils.today(),
        #     "business_branch":business_branch.name,
        #     "pos_profile": "eDoor Profile",
        #     "is_closed": 0,
        #     "outlet": "eDoor Outlet",
        #     "doctype": "Working Day",
        # }).insert()
                
        # frappe.db.commit()

    
    return "done"

@frappe.whitelist()
def get_rate_type_info(name):
    return get_rate_type_info_with_cache(name)
    


@frappe.whitelist("POST")
def rename_doc(data):
    doc = frappe.rename_doc(data['doctype'], data['old_name'], data['new_name'])
    if doc:
        return {
            'name': data['new_name']
        }
    
@frappe.whitelist()
def get_city_ledger_amount_summary(filters):
    filters = json.loads(filters)
    filters["start_date"] =getdate(filters["end_date"]).replace(day=1)
 
    sql = """
            select 
                sum(total_amount*(if(type='Debit',1,-1))) as amount 
            from `tabFolio Transaction`
            where
                transaction_type='City Ledger' and 
                transaction_number = %(city_ledger)s and 
                posting_date < %(start_date)s  
        """
    data = frappe.db.sql(sql,filters,as_dict=1)
    opening_balance = 0
    if data:
        opening_balance = data[0]["amount"] or 0
    debit = 0
    credit = 0
    sql = """
            select 
                sum(if(type='Debit',total_amount,0 )) as debit,
                sum(if(type='Credit',total_amount,0 )) as credit 
            from `tabFolio Transaction`
            where
                transaction_type='City Ledger' and 
                transaction_number = %(city_ledger)s and 
                posting_date between  %(start_date)s and %(end_date)s  
        """
    data = frappe.db.sql(sql,filters,as_dict=1)
    if data:
        debit = data[0]["debit"] or 0
        credit= data[0]["credit"] or 0

    return {
        "opening_balance": opening_balance,
        "debit":debit,
        "credit":credit,
        "balance": opening_balance + (debit - credit)
    }
@frappe.whitelist(methods="POST")
def update_photo(data):
    frappe.db.sql("update `tab{}` set photo=%(photo)s where name=%(name)s".format(data["doctype"]), data)
    frappe.msgprint("Upload photo successfully")

@frappe.whitelist()
def update_reservation_stay_and_reservation(reservation_stay, reservation, reservation_folio=None,ignore_validate=False,run_commit = True):
    
    if reservation_folio:
        update_reservation_folio(name=reservation_folio, doc=None, run_commit=run_commit,ignore_validate=ignore_validate)
    #check if user pass array
    
    if isinstance(reservation_stay, list):
        update_reservation_stay (stay_names=list(set(reservation_stay)),run_commit=run_commit)
    else:
        update_reservation_stay (stay_names=[reservation_stay],run_commit=run_commit)
    
    if isinstance(reservation, list):
        for s in list(set(reservation)):
            update_reservation(name=s, doc=None, run_commit=run_commit)
    else:
        update_reservation(name=reservation, doc=None, run_commit=run_commit)



    
def validate_role(role_name, message = None,is_backdate_transaction =True):

    if is_backdate_transaction==True:
        #check if edoor setting config allow enter back date transaction
        if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")==1: 
            #check user permission if have permission for back date
            role = frappe.db.get_single_value("eDoor Setting",role_name)
            if role:
                if not role in frappe.get_roles(frappe.session.user):
                    frappe.throw(message or "You don't have permission to perform this action")
            else:
                frappe.throw(message or "You don't have permission to perform this action")

       
    
def check_user_permission(role_field_name,message = None):
    role = frappe.db.get_single_value("eDoor Setting",role_field_name)
    
    if role:
        if not role in frappe.get_roles(frappe.session.user):
            frappe.throw(message or "You don't have permission to perform this action")
    else:
        frappe.throw(message or "You don't have permission to perform this action")

def validate_backdate_permission():
    check_user_permission("role_for_back_date_transaction","Sorry you don't have permission to perform back date transaction")

@frappe.whitelist()
def can_view_rate():
    can_see_rate_role = frappe.db.get_single_value("eDoor Setting","can_see_rate_and_amount_role")
    roles = frappe.get_roles(frappe.session.user)
    
    return 1 if can_see_rate_role in roles else 0


    
@frappe.whitelist(methods="POST")
def update_doctype_data(data):
    data["modified_by"] = frappe.session.user
    data["modified"] = frappe.utils.now()
    

    keys = data.keys()
    data_keys = []
    for k in [d for d in keys if d not in ["name","doctype"]]:
        data_keys.append("{0}=%({0})s".format(k))
    if len(data_keys)>0:
        sql ="update `tab{}` set {} where name=%(name)s".format(data["doctype"],",".join(data_keys))
        frappe.db.sql(sql, data)
        frappe.db.commit()

    return frappe.get_doc(data["doctype"],data["name"])

    
def get_months(start_date,end_date):
	months = [{'month_number': dt.month, 'month_name': dt.strftime('%B'),"year": dt.year, "total_day":  calendar.monthrange(dt.year, dt.month)[1]} for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]
	return months

def add_audit_trail(data,update_creation_date=False):
    for d in data:
        if not hasattr(d,"custom_property"):
            doc = frappe.get_doc(d["reference_doctype"],d["reference_name"])
            if hasattr(doc,"property"):
                working_day = get_working_day(doc.property)
                d["custom_posting_date"]= working_day["date_working_day"]
                
                if working_day["cashier_shift"]:
                    d["custom_cashier_shift"]= working_day["cashier_shift"]["name"]
                d["custom_property"]= doc.property
            elif hasattr(doc,"business_branch"):
                working_day = get_working_day(doc.business_branch)
                
                d["custom_posting_date"]= working_day["date_working_day"]
                d["custom_property"]= doc.business_branch
                if working_day["cashier_shift"]:
                    d["custom_cashier_shift"]= working_day["cashier_shift"]["name"]

        d["doctype"]="Comment"
        if not hasattr(d,"comment_type"):
            d["comment_type"]="Info"
            
        d["custom_is_audit_trail"]=1
        d["comment_by"]:frappe.session.user_fullname

        doc = frappe.get_doc(d).insert(ignore_permissions=True,ignore_links=True)
        if update_creation_date:
            frappe.db.sql("update `tabComment` set creation=%(creation)s where name=%(name)s",{"name":doc.name, "creation":d["creation"]})
            





@frappe.whitelist()
def get_deposit_ledger_detail(name):
	doc =frappe.get_doc("Deposit Ledger", name)
	related_ids = [name]
	folio_transaction_ids = frappe.db.get_list("Folio Transaction", filters={"transaction_type":"Deposit Ledger","transaction_number":name} ,page_length=10000,  pluck='name')
	related_ids = related_ids + folio_transaction_ids

	
	return {
		"deposit_ledger":doc,
		"related_ids":related_ids
	}




#i'm piseth add under code

@frappe.whitelist()
def get_desk_folio_detail(name):
	doc =frappe.get_doc("Desk Folio", name)
	related_ids = [name]
	folio_transaction_ids = frappe.db.get_list("Folio Transaction", filters={"transaction_type":"Desk Folio","transaction_number":name} ,page_length=10000,  pluck='name')
	related_ids = related_ids + folio_transaction_ids

	
	return {
		"desk_folio":doc,
		"related_ids":related_ids
	}  


#i'm piseth add under code

@frappe.whitelist()
def get_payable_ledger_detail(name):
	doc =frappe.get_doc("Payable Ledger", name)
	related_ids = [name]
	folio_transaction_ids = frappe.db.get_list("Folio Transaction", filters={"transaction_type":"Payable Ledger","transaction_number":name} ,page_length=10000,  pluck='name')
	related_ids = related_ids + folio_transaction_ids

	
	return {
		"payable_ledger":doc,
		"related_ids":related_ids
	} 


@frappe.whitelist()
def get_reservation_folio_detail(name):
	doc =frappe.get_doc("Reservation Folio", name)
	related_ids = [name]
	folio_transaction_ids = frappe.db.get_list("Folio Transaction", filters={"transaction_type":"Reservation Folio","transaction_number":name} ,page_length=10000,  pluck='name')
	related_ids = related_ids + folio_transaction_ids

	
	return {
		"reservation_folio":doc,
		"related_ids":related_ids
	}  

@frappe.whitelist(methods="POST")
def sort_parent_account_code(parent_account_code, account_codes):
    for d in account_codes:
        sort_order = (account_codes.index(d) + 1) * 100
        sort_order = frappe.db.get_value("Account Code",parent_account_code,"sort_order") + sort_order
        
        frappe.db.sql("update `tabAccount Code` set sort_order={} where name='{}'".format(sort_order, d))
    frappe.db.commit()
    frappe.msgprint("Update parent account code sort order successfully")


@frappe.whitelist()
def update_account_code_to_folio_transaction():
    sql="""
        update `tabFolio Transaction` set parent_account_code = (select parent_account_code from `tabAccount Code` t where t.name = account_code )
    """
    frappe.db.sql(sql)
    #update parent account name
    sql="""
        update `tabFolio Transaction` f set parent_account_name = (select account_name from `tabAccount Code` t where t.name = f.parent_account_code )
        
    """
    frappe.db.sql(sql)

    #update account grouup code
    sql="""
        update `tabFolio Transaction` f set account_group = (select parent_account_code from `tabAccount Code` t where t.name = f.parent_account_code )
    """
    frappe.db.sql(sql)

    #update account grouup name
    sql="""
        update `tabFolio Transaction` f set account_group_name = (select account_name from `tabAccount Code` t where t.name = f.account_group )
    """
    frappe.db.sql(sql)
   
    #update report quantity
    sql="""
        update `tabFolio Transaction` f set report_quantity = if((select show_quantity_in_report from `tabAccount Code` t where t.name = f.account_code )=1,f.quantity,0)
    """
    frappe.db.sql(sql)
   
    #Update flash report revenue group
    sql="""
         update `tabFolio Transaction` f set flash_report_revenue_group = (select flash_report_revenue_group from `tabAccount Code` t where t.name = f.account_code )
    """
    frappe.db.sql(sql)
    # update parent account name to account code doctye
    sql="""
         update `tabAccount Code` a
         join `tabAccount Code` b on a.parent_account_code = b.name
         set
            a.parent_account_name = b.account_name
            
    """
    frappe.db.sql(sql)
    sql="""
         update `tabAccount Code` a
         join `tabAccount Code` b on a.account_group = b.name
         set
            a.account_group_name = b.account_name
            
    """
    
    frappe.db.sql(sql)
    sql = """
        update `tabRevenue Forecast Breakdown` a 
        join `tabAccount Code` b on b.name = a.account_code
        SET
            a.account_category = b.account_category,
            a.type = b.type,
            a.parent_account_code = b.parent_account_code,
            a.parent_account_name = b.parent_account_name,
            a.account_group_code = b.account_group,
            a.account_group_name = b.account_group_name
    """
    
    frappe.db.sql(sql)
    frappe.db.commit()

  

    frappe.db.commit()
    return "Done"

@frappe.whitelist()
def update_account_category_information_to_folio_transaction():
    sql="""
        UPDATE `tabFolio Transaction` t
        JOIN `tabAccount Category` c ON t.account_category = c.name
        SET t.account_category_sort_order = c.sort_order
    """
    frappe.db.sql(sql)


    frappe.db.commit()
    return "Done"
    

@frappe.whitelist(methods="POST")
def sort_child_account_code(account_codes):
    for d in account_codes:
        sort_order = account_codes.index(d) + 1

        sort_order = frappe.db.get_value("Account Code",d["parent"],"sort_order") + sort_order
        frappe.db.sql("update `tabAccount Code` set sort_order={} where name='{}'".format(sort_order, d["account_code"]))
        frappe.db.sql("update `tabFolio Transaction` set account_code_sort_order={} where account_code='{}'".format(sort_order, d["account_code"]))

    frappe.db.commit()
    frappe.msgprint("Update child account code sort order successfully")

@frappe.whitelist(methods="POST")
def sort_account_categories(account_categories):
    for d in account_categories:
        sort_order = (account_categories.index(d) + 1) * 100
        frappe.db.sql("update `tabAccount Category` set sort_order={} where name='{}'".format(sort_order, d))

        frappe.db.sql("update `tabFolio Transaction` set account_category_sort_order={} where account_category='{}'".format(sort_order, d))

    frappe.db.commit()
    frappe.msgprint("Update parent account code sort order successfully")


@frappe.whitelist()
def get_cashier_shift_summary(name,property):
    doc = frappe.get_doc("Cashier Shift",name)
    #Get cash payment
    sql = """
        select 
            sum(amount * if(type='Debit',1,0)) as cash_debit, 
            sum(amount * if(type='Debit',0,1)) as cash_credit
        from   `tabFolio Transaction`
        where
            cashier_shift = %(cashier_shift)s and 
            payment_type_group ='Cash' and 
            property=%(property)s
        """
    data = frappe.db.sql(sql,{"property":property,"cashier_shift":name},as_dict=1)
    sql = """
        select 
            payment_type_group,
            payment_type,
            sum(amount * if(type='Debit',1,0)) as total_debit,
            sum(amount * if(type='Debit',0,1)) as total_credit,
            sum(amount * if(type='Debit',-1,1)) as total,
            0 as actual_close_amount
        from   `tabFolio Transaction`
        where
            cashier_shift = %(cashier_shift)s and 
            payment_type <> '' and  
            property=%(property)s
        group by 
            payment_type_group,
            payment_type
    """
    summary_by_payment_type = frappe.db.sql(sql,{"property":property,"cashier_shift":name}, as_dict=1) 

    #payment transaction summary
    sql = """
        select 
            account_code,
            account_name,
            sum(amount * if(type='Debit',1,0)) as total_debit,
            sum(amount * if(type='Debit',0,1)) as total_credit
        from   `tabFolio Transaction`
        where
            cashier_shift = %(cashier_shift)s and 
            ifnull(payment_type,'') <> '' and  
            property=%(property)s
        group by 
            account_code,
            account_name,
            type
    """
    payment_transaction_summary = frappe.db.sql(sql,{"property":property,"cashier_shift":name}, as_dict=1) 
    

    expected_cash = []
    for d in doc.cash_float:
        if d.payment_type_group =="Cash":
            expected_amount = d.input_amount
            if d.currency == frappe.db.get_single_value("ePOS Settings","currency"):
                expected_amount =  ((d.input_amount or 0) + (data[0]["cash_credit"] or 0)) - ( data[0]["cash_debit"] or 0)


            expected_cash.append({
                "currency":d.currency,
                "pos_currency_format":d.pos_currency_format,
                "payment_type":d.payment_method,
                "expected_amount":expected_amount,
                "precision":d.currency_precision,
                "local":d.locale,
                "exchange_rate": d.exchange_rate
            })


    return {
        "opening_cash_float": doc.total_opening_amount,
        "cash_debit": data[0]["cash_debit"],
        "cash_credit": data[0]["cash_credit"],
        "cash_in_hand": ((doc.total_opening_amount or 0) + (data[0]["cash_credit"] or 0)) - ( data[0]["cash_debit"] or 0),
        "summary_by_payment_type":summary_by_payment_type,
        "payment_transaction_summary":payment_transaction_summary,
        "expected_cash":expected_cash


    }


@frappe.whitelist()
def get_cash_count_setting(property):
    base_currency = frappe.db.get_single_value("ePOS Settings", "currency")
    base_currency_doc = frappe.get_doc("Currency", base_currency)
    data =  frappe.get_doc("eDoor Setting").cash_count_setting
    return_date = []
    exchange_rate_data = []
    currencies = set([d.currency for d in data if d.currency != base_currency])
    for c in currencies:
        to_currency_doc =  frappe.get_doc("Currency", c)
        exchange_rate_data.append({
            "base_currency": base_currency,
            "to_currency": c,
            "exchange_rate":  get_current_exchange_rate(property=property, base_currency= base_currency,second_currency = c),
            "precision":to_currency_doc.custom_currency_precision,
            "locale": to_currency_doc.custom_locale,
            "pos_currency_format": to_currency_doc.custom_pos_currency_format
        })

    for d in data:
     
        return_date.append({
            "currency": d.currency,
            "precision":base_currency_doc.custom_currency_precision if   d.currency == base_currency else [c for c in exchange_rate_data if c["to_currency"] == d.currency][0]["precision"],
            "pos_currency_format": base_currency_doc.custom_pos_currency_format if   d.currency == base_currency else  [c for c in exchange_rate_data if c["to_currency"] == d.currency][0]["pos_currency_format"],
            "label": d.label,
            "value": d.value,
            "exchange_rate":  1 if d.currency == base_currency else [c for c in exchange_rate_data if c["to_currency"] == d.currency][0]["exchange_rate"]
        })
      
    return {
        "cash_count_setting":return_date,
        "exchange_rate_data": exchange_rate_data
    }

def get_current_exchange_rate(property, base_currency, second_currency):
    sql = "select exchange_rate from `tabCurrency Exchange` where custom_business_branch=%(property)s and  from_currency='{}' and to_currency = '{}' and docstatus=1  order by posting_date desc, modified desc limit 1"
    data = frappe.db.sql(sql.format(base_currency, second_currency),{"property":property},as_dict=1)
    if len(data)> 0:
        return data[0]["exchange_rate"]
    else:
        return 1
    

def update_is_arrival_date_in_room_rate(stay_name,run_commit = True):
    sql ="""
        update `tabReservation Room Rate` 
        set is_arrival = 0 
        where reservation_stay = '{0}' and is_arrival=1
    """.format(stay_name)
    frappe.db.sql(sql)

    first_stay_date = frappe.db.sql( "select name from `tabReservation Room Rate` x where x.reservation_stay = '{0}' order by x.date limit 1".format(stay_name),as_dict=1)
    if len(first_stay_date)>0:
        sql ="""update `tabReservation Room Rate` 
                set is_arrival = 1 
            where 
            name='{}'
        """.format(first_stay_date[0]["name"])
        frappe.db.sql(sql)
        
    if run_commit:
        frappe.db.commit()


@frappe.whitelist()
def get_report_config(property,report):
    if not property:
        property = frappe.defaults.get_user_default("business_branch")
    if not property:
        business_branch = frappe.db.get_list("Business Branch",pluck="name")
        if business_branch:
            property = business_branch[0]
    if not property:
        return {}
   
    return frappe.get_last_doc("Report Configuration", filters={"property":property, "report":report} )

@frappe.whitelist()
def update_room_status_by_reservation_stay(name):
    if name:
        stay_doc = frappe.get_doc("Reservation Stay", name)
        working_day = get_working_day(stay_doc.property)
        room_list = frappe.db.sql("""select 
                                        room_id,
                                        min(date) as date 
                                    from `tabRoom Occupy` 
                                    where 
                                        reservation_stay= '{}' and 
                                        date <= '{}'
                                    group by
                                        room_id
                                  """.format(name, working_day['date_working_day']),as_dict=1)
        
        for r in room_list:
            room_doc= frappe.get_doc("Room",r["room_id"])
            if getdate(r["date"])<working_day["date_working_day"]:
                room_doc.room_status = "Vacant"
            else:
                room_doc.room_status = "Occupy"
            room_doc.save(ignore_permissions=True)
            
        frappe.db.commit()



@frappe.whitelist()
def get_tax_invoice_data(folio_number,document_type,date = None):
    data=frappe.db.sql("select * from `tabFolio Transaction` where transaction_number='{}' and transaction_type='Reservation Folio' and parent_account_name!='POS Transfer'".format(folio_number),as_dict=1)
    sale=frappe.db.sql("select * from `tabSale` where name='{}'".format(folio_number),as_dict=1)
    
    tax_data = []
    pos_tax_data = get_tax_invoice_data_from_pos_bill_to_room(document_type, folio_number)
    if document_type == 'Reservation Folio':
        tax_data = get_tax_data(data)
        tax_data = tax_data + pos_tax_data["revenue_data"]
    elif document_type == 'Sale':
        tax_data = get_tax_from_sale(sale)
    property = frappe.db.get_value("Tax Invoice", {'document_name':folio_number},"property")
    exchange_rate = frappe.db.get_value("Tax Invoice",{'document_name':folio_number},"exchange_rate")
    if not date:
        working_day = get_working_day(property)
        date = working_day["date_working_day"]
    if (exchange_rate or 0) == 0:
        exchange_rate = get_exchange_rate(property,date)

    tax_summary = get_tax_summary(data + pos_tax_data["tax_summary_raw_data"])
    
    if document_type == 'Reservation Folio':
        total_vat = get_tax_invoice_vat_amount(data) 
    elif document_type == 'Sale':
        # tax 3 is alway vat
        total_vat = sale[0]["tax_3_amount"] or 0
        
        
    
    # total tax vat from pos bill to room
    total_vat = total_vat + sum([d["tax_3_amount"] for d in pos_tax_data["revenue_data"]])
    
    grand_total = sum(d["quantity"] * d["price"]  for d in tax_data) + sum(d["child_total"] for d in tax_summary)  + total_vat
    
    return_data = {
        "property":property,
        "document_type":document_type,
        "data":tax_data,
        "summary":tax_summary,
        "taxable_amount": sum(d["quantity"] * d["price"]  for d in tax_data),
        "vat":{
            "description":"អាករលើតម្លៃបន្ថែម/VAT (10%)",
            "value":total_vat
        },

        "grand_total":grand_total, 
        "exchange_rate":exchange_rate ,
        "grand_total_second_currency":grand_total*exchange_rate 
    }
    
    return return_data

@frappe.whitelist(allow_guest=True)
def get_exchange_rate(property,date=None):
    if not date:
        working_day = get_working_day(property)
        date = working_day["date_working_day"]
        
    main_currency = frappe.db.get_single_value("ePOS Settings","currency")
    second_currency = frappe.db.get_single_value("ePOS Settings","second_currency")    
    data=frappe.db.sql("select exchange_rate from `tabCurrency Exchange` where from_currency='{}' and to_currency='{}' and custom_business_branch=%(property)s and posting_date<='{}'".format(main_currency, second_currency,date),{"property":property},as_dict=1)
    if data:
        return data[0]["exchange_rate"] or 1 
    else:
        return 1
    
def get_tax_from_sale(data):
    sql ="""
            select 
                product_name  as description,
                product_name_kh ,
                `portion`,
                is_free,
                modifiers,
                discount,
                discount_amount,
                discount_type,
                sum(quantity) as quantity,
                price,
                sum(amount) as amount  
            from `tabSale Product` 
            where 
                parent='{}' and
                total_tax > 0
            group by 
                product_name,
                product_name_kh,
                `portion`,
                is_free,
                modifiers,
                discount,
                discount_amount,
                discount_type, 
                price 
        
            """.format(data[0]['name'])
    
    sale_products = frappe.db.sql(sql, as_dict=1)
    return sale_products

def get_tax_data(data):
    from itertools import groupby
    raw_data = []
    for d in data:
        tax_invoice_group_by_key , tax_invoice_description_template,show_in_tax_invoice,sort_order = frappe.db.get_value("Account Code",d["account_code"], ["tax_invoice_group_by_key ", "tax_invoice_description_template","show_in_tax_invoice","sort_order"])
        
        if show_in_tax_invoice:
            record = {}
            if tax_invoice_group_by_key:
                record["group_by_key"] = frappe.render_template(tax_invoice_group_by_key,{"doc":d})
            else:
                record["group_by_key"] = d["report_description"]
                
            if tax_invoice_description_template:
                record["description"] = frappe.render_template(tax_invoice_description_template,{"doc":d,"frappe":frappe})
            else:
                record["description"] = d["report_description"]
                
            record["quantity"] = d["report_quantity"] * (1 if d["type"] =="Debit" else -1) 
            record["amount"] = (d["amount"] - d["discount"]) * (1 if d["type"] =="Debit" else -1) 
            record["sort_order"] = sort_order 
            
            raw_data.append(record)
            
    raw_data.sort(key=lambda x: x["group_by_key"])
    # Group the data by the group_by_key field
    grouped_data = {key: list(group) for key, group in groupby(raw_data, key=lambda x: x["group_by_key"])}
    
    return_data =[]
    for key, group in grouped_data.items():
        record={
            "description":group[0]["description"],
            "sort_order":group[0]["sort_order"],
            "quantity":sum(d["quantity"] for d in group),
            "amount":sum(d["amount"] for d in group)
        }
        record["price"] =  record["amount"] /(1 if (record["quantity"] or 0 )==0 else record["quantity"])
       
        
        return_data.append(record)
        
    return  sorted(return_data, key=lambda x: x['sort_order'])


def get_tax_summary(data):
    
    raw_data = []
    for d in data:
        tax_invoice_summary_key = frappe.db.get_value("Account Code",d["account_code"],"tax_invoice_summary_key")
        if tax_invoice_summary_key:
            record = {"tax_invoice_summary_key":tax_invoice_summary_key}
            record["amount"] = (d["amount"] - d["discount"]) * (1 if d["type"] =="Debit" else -1) 
            
            raw_data.append(record)

    tax_summary_group = frappe.db.sql("select total_label,alias,is_group, parent_tax_invoice_summary_group, name, label,tax_report_fieldname from `tabTax Invoice Summary Group` order by sort_order",as_dict=1)
    
    # return data
    # loop group
    return_data = []
    for g in [d for d in tax_summary_group if d["is_group"]==1]:
        value = sum([d["amount"] for d in raw_data if d["tax_invoice_summary_key"]==g["name"]])
       
        if value>0:
            record = {
                "label":g["label"],
                "value":value
            }
            
            
            # get children
            children=[]
            children_alias=[]
            for c in [d for d in tax_summary_group if d["parent_tax_invoice_summary_group"]==g["name"]]:
                if c["alias"]:
                    children_alias.append(c["alias"])
                value = sum([d["amount"] for d in raw_data if d["tax_invoice_summary_key"]==c["name"]])
                if value>0:
                    children.append({
                        "label":c["label"],
                        "fieldname":c["tax_report_fieldname"],
                        "value":value
                    })
            if children:
                record["children"]=children  
                record["child_total"] =   sum([d["value"] for d in record["children"]]) 
                record["total"] = {
                    "label":"{} {}".format(g["total_label"], get_comma_and(children_alias)) ,
                    "value":record["value"] +(record["child_total"] or 0)
                }
            else:
                record["child_total"] = 0
            return_data.append(record)
    
           
    return return_data


def get_tax_invoice_vat_amount(data):
    # xxx
    amount = 0
    for d in data:
        if frappe.db.get_value("Account Code",d["account_code"], "is_vat")==1:
            amount = amount + (d["amount"] * (1 if d["type"] =="Debit" else -1) )
            
    return amount or 0
        

@frappe.whitelist()
def get_commercial_tax_invoice_data(folio_number,document_type,date = None):
    data=frappe.db.sql("select * from `tabFolio Transaction` where transaction_number='{}' and transaction_type='Reservation Folio' and is_base_transaction=1 and account_group_name='Charge'".format(folio_number),as_dict=1)
    
    tax_data = []
    if document_type == 'Reservation Folio':
        tax_data = get_commercial_tax_data(data)
    property = frappe.db.get_value("Tax Invoice", {'document_name':folio_number},"property")
    exchange_rate = frappe.db.get_value("Tax Invoice",{'document_name':folio_number},"exchange_rate")
    if not date:
        working_day = get_working_day(property)
        date = working_day["date_working_day"]
    if (exchange_rate or 0) == 0:
        exchange_rate = get_exchange_rate(property,date)

    
    
    if document_type == 'Reservation Folio':
        total_vat = get_tax_invoice_vat_amount(data) 
        
        

    return_data = {
        "property":property,
        "document_type":document_type,
        "data":tax_data,

        "exchange_rate":exchange_rate ,

    }
    
    return return_data
   
   

def get_commercial_tax_data(data):
    from itertools import groupby

    raw_data = []
    for d in data:
        tax_invoice_group_by_key , tax_invoice_description_template,show_in_tax_invoice,sort_order = frappe.db.get_value("Account Code",d["account_code"], ["tax_invoice_group_by_key", "tax_invoice_description_template","show_in_tax_invoice","sort_order"])
        
        if show_in_tax_invoice:
            record = {}
            if tax_invoice_group_by_key:
                record["group_by_key"] = frappe.render_template(tax_invoice_group_by_key,{"doc":d})
            else:
                record["group_by_key"] = d["report_description"]
                
            if tax_invoice_description_template:
                record["description"] = frappe.render_template(tax_invoice_description_template,{"doc":d,"frappe":frappe})
            else:
                record["description"] = d["report_description"]
                
            record["quantity"] = d["report_quantity"] * (1 if d["type"] =="Debit" else -1) 
            record["amount"] = (d["transaction_amount"] - d["discount"]) * (1 if d["type"] =="Debit" else -1) 
            record["sort_order"] = sort_order 
            
            raw_data.append(record)
            
            
    raw_data.sort(key=lambda x: x["group_by_key"])
    # Group the data by the group_by_key field
    grouped_data = {key: list(group) for key, group in groupby(raw_data, key=lambda x: x["group_by_key"])}

    return_data =[]
    for key, group in grouped_data.items():
        record={
            "description":group[0]["description"],
            "sort_order":group[0]["sort_order"],
            "quantity":sum(d["quantity"] for d in group),
            "amount":sum(d["amount"] for d in group)
        }
        record["price"] =  record["amount"] /(1 if (record["quantity"] or 0 )==0 else record["quantity"])
       
        
        return_data.append(record)
        
    return  sorted(return_data, key=lambda x: x['sort_order'])
     
def get_comma_and(data):
    return frappe.utils.comma_and(data, add_quotes=False).replace(" and ", " & ")

@frappe.whitelist()
def get_tax_invoice_data_from_pos_bill_to_room(transaction_type,transaction_number):
    
    sale_numbers = frappe.db.sql("select sale from `tabFolio Transaction` where transaction_type='{}' and transaction_number='{}'  and coalesce(sale,'')!=''".format(transaction_type,transaction_number),as_dict=1)
    
    revenue_data = get_sale_data_group_by_revenue_group([d["sale"] for d in sale_numbers])
    tax_raw_data = []
    
    for r in revenue_data:
        pos_account_code_config = get_pos_account_code_config(r["outlet"],r["shift_name"])
        #  get account  for charge revenue group
        account_codes = [d.account_code for d in pos_account_code_config.pos_revenue_account_codes if d.revenue==r["revenue_group"]]
        
        if account_codes:
            r["description"] = frappe.db.get_value("Account Code", account_codes[0],"account_name")
        tax_raw_data.append({"account_code":account_codes[0],"amount":r["price"],"discount":r["discount"],"type":"Debit" })
        if r["tax_1_amount"]:
            tax_raw_data.append({"account_code":pos_account_code_config.tax_1_account,"amount":r["tax_1_amount"],"discount":0,"type":"Debit" })
            
        if r["tax_2_amount"]:
            tax_raw_data.append({"account_code":pos_account_code_config.tax_2_account,"amount":r["tax_2_amount"],"discount":0,"type":"Debit" })
            
            
            
    return {"revenue_data":revenue_data,"tax_summary_raw_data":tax_raw_data or []}


def get_sale_data_group_by_revenue_group(sale_numbers):
    if sale_numbers:
        sql="""
            select 
                sp.revenue_group, 
                s.outlet,
                s.shift_name,
                sum(sp.sub_total) as price, 
                sum(sp.total_discount) as discount,
                1 as quantity ,
                sum(sp.sub_total) as amount,
                sum(sp.tax_1_amount) as tax_1_amount,
                sum(sp.tax_2_amount) as tax_2_amount,
                sum(sp.tax_3_amount) as tax_3_amount,
                9999999 as sort_order
            from `tabSale Product`  sp
                inner join `tabSale` s on s.name = sp.parent
            where 
                sp.parent in %(sale_numbers)s and 
                coalesce(sp.total_tax,0)>0 
            group by 
                revenue_group,
                outlet,
                shift_name
        """
        data = frappe.db.sql(sql,{"sale_numbers":sale_numbers},as_dict=1)
        return data
    else:
        return []

 


@lru_cache(maxsize=128)
def get_pos_account_code_config(outlet, shift_name):
    data = frappe.db.get_list("POS Account Code Config", filters={"outlet":outlet, "shift_name":shift_name})
    if data:
        return frappe.get_doc("POS Account Code Config", data[0].name)
    return None
    



@frappe.whitelist(methods="POST")
def generate_tax_invoice(property=None,document_type=None, folio_number=None,tax_invoice_date=None,tax_invoice_type=None,exchange_rate=4000):
    # if frappe.db.get_value("Reservation Folio",folio_number,"tax_invoice_number"):
    #     frappe.throw("This folio number is already generate tax invoice")
    # if not frappe.db.get_value("Folio Transaction",folio_number,"transaction_number"):
    #     frappe.throw("This folio number No Transaction") 

    # tax_invoice_format = frappe.db.get_value("Business Branch",property,"tax_invoice_number_format")
    # from frappe.model.naming import make_autoname
    # tax_invoice_number = make_autoname(tax_invoice_format)
    if not tax_invoice_type:
        frappe.throw("Please enter tax invoice type.")
    if not exchange_rate:    
        exchange_rate  = get_exchange_rate(property, tax_invoice_date)
    
    doc =frappe.get_doc(document_type,folio_number)
    if frappe.db.exists("Tax Invoice",{"document_type":document_type,"document_name":folio_number}):
        frappe.throw("This folio number # {} is already generate tax invoice.".format(folio_number))
        
    tax_invoice_doc = frappe.get_doc({
        "doctype":"Tax Invoice",
        "property":property,
        "tax_invoice_type":tax_invoice_type,
        "tax_invoice_date":tax_invoice_date,
        "exchange_rate":exchange_rate,
        "document_type":document_type,
        "document_name":folio_number,
        "guest":doc.guest
    })
    
    tax_invoice_doc.insert()
    
    
    
    sql="update `tab{}` set is_generate_tax_invoice=1, tax_invoice_number=%(tax_invoice_number)s, tax_invoice_date=%(tax_invoice_date)s , exchange_rate=%(exchange_rate)s where name=%(name)s".format(document_type)
    frappe.db.sql(sql,{ "name":folio_number,"tax_invoice_number":tax_invoice_doc.name, "exchange_rate":exchange_rate,"tax_invoice_date":tax_invoice_date})
    
    update_tax_invoice_data_to_tax_invoice(tax_invoice_name=tax_invoice_doc.name,run_commit=False)
    
    
    frappe.db.commit()
    frappe.msgprint(_("Generate tax invoice successfully"))
    
    
    return tax_invoice_doc
@frappe.whitelist()
def update_tax_invoice_data_to_tax_invoice(tax_invoice_name,run_commit=True):
    
    doc = frappe.get_doc("Tax Invoice",tax_invoice_name)
    tax_data = get_tax_invoice_data(folio_number = doc.document_name, document_type=doc.document_type, date= doc.tax_invoice_date)
    
    doc.sub_total = sum([d["quantity"] * d["price"]  for d in tax_data["data"]])
    
    # service charge
    doc.service_charge = sum(
                d["value"]
                for entry in tax_data["summary"] if "children" in  entry
                for d in entry["children"] if d["fieldname"] =='service_charge'
            )
    
    # accommodation_tax
    doc.accommodation_tax = sum(
                d["value"]
                for entry in tax_data["summary"] if "children" in  entry
                for d in entry["children"] if d["fieldname"] =='accommodation_tax'
            )
    
    # specific_tax
    doc.specific_tax = sum(
                d["value"]
                for entry in tax_data["summary"] if "children" in  entry
                for d in entry["children"] if d["fieldname"] =='specific_tax'
            )
    
   
    doc.vat = tax_data["vat"]["value"]
    
    doc.grand_total = tax_data["grand_total"]
    doc.flags.ignore_validate = True
    doc.flags.ignore_on_update = True
    
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
    return doc
    
    

@frappe.whitelist()
def get_generate_tax_invoice_information(property,posting_date=None):
    if not posting_date:
        working_day = get_working_day(property)
        posting_date = working_day["date_working_day"]
        
    from frappe.model.naming import NamingSeries,make_autoname
    raw_prefix = frappe.db.get_value("Business Branch",property,"tax_invoice_number_format")
    prefix = raw_prefix.replace("#","").replace(".","")
    current_counter= NamingSeries(prefix).get_current_value()
    second_currency=frappe.db.get_single_value("ePOS Settings","second_currency")
    precision,custom_pos_currency_format = frappe.db.get_value("Currency",second_currency,["custom_currency_precision","custom_pos_currency_format"])
    data = {
        "current_counter":current_counter,
        "next_tax_invoice_number": make_autoname(raw_prefix),
        "exchange_rate":get_exchange_rate(property, posting_date),
        "base_currency":frappe.db.get_single_value("ePOS Settings","currency"),
        "second_currency":{
            "currency":second_currency,
            "precision": precision,
            "pos_currency_format":custom_pos_currency_format
        }
    }
    
    return data
    
    

@frappe.whitelist()
def get_package_detail(rate_type=None,property=None, business_source=None,date=None):
    rate_type_doc = frappe.get_doc("Rate Type", rate_type)
    package_account_code_doc = frappe.get_doc("Account Code",rate_type_doc.account_code)
    return {
        "rate_type":rate_type_doc,
        "account_code":package_account_code_doc
    }
    
    

def get_breakdown_package_charge_code(stay_doc, room_rate,posting_rules=[]):
    package_charge_codes = []
    if stay_doc.inclusion_items:

        for p in [d for d in stay_doc.inclusion_items if d.posting_rule in posting_rules]:
            charge = {"account_code":p.account_code}
            
            if p.charge_rule=="Stay":
                charge["rate"] = p.rate
                charge["quantity"] =1
                charge["adult"] =room_rate.adult
                charge["child"] =room_rate.child
                package_charge_codes.append(charge)
                
            elif p.charge_rule=="Pax":
                if room_rate.adult:
                    charge["rate"] = p.adult_rate
                    charge["quantity"] =room_rate.adult
                    charge["adult"] =room_rate.adult
                    charge["child"] =0
                    package_charge_codes.append(copy.deepcopy(charge))
                if room_rate.child:
                    charge["rate"] = p.child_rate
                    charge["quantity"] =room_rate.child
                    charge["child"] =room_rate.child
                    charge["adult"] =0
                    package_charge_codes.append(copy.deepcopy(charge))
                
            elif p.charge_rule=="Adult":
                charge["rate"] = p.adult_rate
                charge["quantity"] =room_rate.adult
                charge["adult"] =room_rate.adult
                charge["child"] =0
                package_charge_codes.append(charge)
                
            elif p.charge_rule=="Child":
                charge["rate"] = p.child_rate
                charge["quantity"] =room_rate.child
                charge["child"] =room_rate.child
                charge["adult"] =0
                package_charge_codes.append(charge)
            
            
            
        
        return package_charge_codes
    
    return []

def get_reservation_stay_additional_information(stay_names):
    sql ="""select 
        name,
        property,
        reservation_type,
        reservation_status,
        business_source, 
        business_source_type, 
        checked_in_system_date,
        arrival_date,
        departure_date,
        is_early_checked_out,
        require_pickup as is_pickup,
        require_drop_off as is_drop_off,
        rate_type,
        is_complimentary,
        is_house_use,
        is_walk_in ,
        guest,
        guest_name,
        guest_type,
        nationality,
        is_active_reservation,
        tax_rule,
        rate_include_tax,
        tax_1_rate,
        tax_2_rate,
        tax_3_rate
    from `tabReservation Stay` 
    where name in %(stay_names)s"""
    return frappe.db.sql(sql,{"stay_names":stay_names},as_dict=1)
    

    

@frappe.whitelist()
def get_folio_transaction_without_breakdown(property, start_date,end_date,account_code=None):
    sql = """
        select 
            name,
            posting_date,
            is_base_transaction,
            account_code,
            account_name,
            transaction_amount as amount,
            parent_reference,
            type,
            folio_type,
            guest,
            guest_name,
            cashier_shift,
            business_source,
            room_number,
            room_type,
            room_type_alias,
            account_code_sort_order,
            creation,
            owner,
            coalesce(note,'') as note
        from `tabFolio Transaction`
        where
            is_base_transaction = 1  and 
            property = %(property)s and 
            posting_date between %(start_date)s and %(end_date)s
        
    """
    account_codes=[]
    if account_code:
        account_codes = get_doctype_tree_name("Account Code" ,account_code ,"parent_account_code")
        account_codes.append(account_code)
        sql = sql +  " and account_code in %(account_codes)s"
    
    data = frappe.db.sql(sql,{"property":property,"start_date":start_date,"end_date":end_date,"account_codes":account_codes},as_dict=1)
    
    return_data = [d for d in data if d["is_base_transaction"]==1]
    for t in return_data:
        t["amount"] = t["amount"]  + sum([d["amount"] * (1 if d["type"]=='Debit' else -1)  for d in data  if d["is_base_transaction"] == 0 and d["parent_reference"] ==t["name"]])
        
    group_data = { (item["account_code"], item["account_name"], item["account_code_sort_order"], item["posting_date"]) for item in return_data }
    sorted_group_data = sorted(group_data, key=lambda x: x[2])
    sorted_group_data =[
                    {"account_code": item[0], "account_name": item[1],"posting_date":item[3]}
                    for item in sorted_group_data
                ]
     
    return {"group_data": sorted_group_data, "data":return_data}
    
@frappe.whitelist()
def ping():
    return "pong"