import datetime
from decimal import Decimal

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

@frappe.whitelist()
def get_working_day(property = ''):
    working_day = frappe.db.sql("select  posting_date as date,name,pos_profile from `tabWorking Day` where business_branch = '{0}' order by creation desc limit 1".format(property),as_dict=1)
    cashier_shift = None
    if len(working_day)>0:
        data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = '{}' and working_day='{}' and pos_profile='{}' ORDER BY creation desc limit 1".format(property,working_day[0]["name"],working_day[0]["pos_profile"]),as_dict=1)
        
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
        if doc.doctype not in ["Note", "Temp Room Occupy","Contact","DocShare","Doctype","DefaultValue","Print Format","Queue Job","System Console","Scheduled Job Log","Route History","Version","Error Log","Scheduled Job Log","Console Log","Activity Log","Comment"]:
            frappe.get_doc({
                "doctype":"Queue Job",
                "document_name":doc.name,
                "document_type":doc.doctype,
                "action":"update_fetch_from_field"
            }).insert()
        
 

 
def update_keyword(doc, method=None, *args, **kwargs):
    skip_doctypes = ["Folio Transaction","City Ledger","Vendor","Customer","Reservation Stay","Reservation","Reservation Stay Room","Room","Room Block","Business Source"]
    if  doc.doctype in skip_doctypes:
        frappe.get_doc({
            "doctype":"Queue Job",
            "document_name":doc.name,
            "document_type":doc.doctype,
            "action":"update_keyword"

        }).insert()

        # frappe.enqueue("edoor.api.utils.update_keyword_queue", queue='long', doc=doc)

    
    




def update_comment_after_insert(doc, method=None, *args, **kwargs):
    if doc.comment_type=="Deleted":
        return
    if doc.comment_type == "Workflow": return
    #if doc have property field then update property, audit_date and is audit trail to true
    update_files = ["comment_by='{}'".format(frappe.db.get_value("User",doc.owner, "full_name"))]
    update_files.append("custom_comment_by_photo='{}'".format(frappe.db.get_value("User",doc.owner, "user_image") or ""))
    
    if not doc.custom_icon:
        icon_data = frappe.db.sql("select icon from `tabApp Icons` where name='{}'".format(doc.custom_audit_trail_type), as_dict=1)
        icon = 'pi pi-stop'
        if icon_data:
            icon = icon_data[0]["icon"]

        update_files.append("custom_icon='{}'".format(icon))
    
    ref_doc = frappe.get_doc(doc.reference_doctype,doc.reference_name )
    if doc.reference_name and not doc.custom_property:
        
        if hasattr(ref_doc, "property"):
            working_day = get_working_day(ref_doc.property)
            update_files.append("custom_property='{}'".format(ref_doc.property))
            update_files.append("custom_posting_date='{}'".format(working_day["date_working_day"]))
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

    
    
    frappe.db.sql("update `tabComment` set {} where name='{}'".format(",".join(update_files), doc.name))
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
def update_reservation(name=None,doc=None, run_commit = True):
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
                    
                    sum(if(is_active_reservation =1,room_nights,0)) as room_nights,
                    sum(if(is_active_reservation=1,total_room_rate,0)) as total_room_rate,
                    avg(if(is_active_reservation=1,adr,0)) as adr,
                    min(if(is_active_reservation=1,room_rate,0)) as room_rate,
                    sum(if(is_active_reservation=1,room_rate_discount,0)) as room_rate_discount,
                    sum(if(is_active_reservation=1,room_rate_tax_1_amount,0)) as room_rate_tax_1_amount,
                    sum(if(is_active_reservation=1,room_rate_tax_2_amount,0)) as room_rate_tax_2_amount,
                    sum(if(is_active_reservation=1,room_rate_tax_3_amount,0)) as room_rate_tax_3_amount,
                    sum(if(is_active_reservation=1,total_room_rate_tax,0)) as total_room_rate_tax,
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
        doc.total_room_rate= data[0]["total_room_rate"]
        doc.room_rate= data[0]["room_rate"]
        doc.adr= data[0]["adr"]
        doc.room_rate_discount= data[0]["room_rate_discount"]
        doc.room_rate_tax_1_amount= data[0]["room_rate_tax_1_amount"]
        doc.room_rate_tax_2_amount= data[0]["room_rate_tax_2_amount"]
        doc.room_rate_tax_3_amount= data[0]["room_rate_tax_3_amount"]
        doc.total_room_rate_tax= data[0]["total_room_rate_tax"]
        
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

    
        

        doc.update_reservation_stay = False
        doc.flags.ignore_on_update= True
        doc.save()
        if run_commit:
            frappe.db.commit()
        return doc

@frappe.whitelist()
def update_reservation_folio(name=None, doc=None,run_commit=True):
    if name:
        doc = frappe.get_doc("Reservation Folio",name)

    sql_folio = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'Reservation Folio' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql_folio, as_dict=1)

    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.save(   ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_deposit_ledger(name=None, doc=None,run_commit=True):

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
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_desk_folio(name=None, doc=None,run_commit=True):

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
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_payable_ledger(name=None, doc=None,run_commit=True):

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
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc


@frappe.whitelist()
def update_reservation_stay(name=None, doc=None,run_commit=True,is_save=True):
    if name or doc:
        if name:
            if not frappe.db.exists("Reservation Stay",name ):
                return
            
            doc = frappe.get_doc("Reservation Stay",name)

        #1 update data to reservation stay room the rest will update from reservation stay validate event
        sql_folio = """
        select  
                account_category as label,
                abs(sum(amount * if(type='Debit',1,-1))) as amount ,
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                reservation_stay = '{}' and 
                transaction_type = 'Reservation Folio'
            group by account_category
        """.format(
                doc.name
            )

        folio_data = frappe.db.sql(sql_folio, as_dict=1)




        
        doc.total_debit =  Enumerable(folio_data).sum(lambda x: x.debit or 0)
        doc.total_credit=  Enumerable(folio_data).sum(lambda x: x.credit or 0)
        

        #REMOVE credit and debit from dict
        for  d in folio_data:
            del d["credit"]
            del d["debit"]
        
        for stay in doc.stays:
            #get rate from first stay of each room_type 

            sql = """
                select 
                    min(rate) as rate,
                    min(input_rate) as input_rate,
                    avg(total_rate) as adr,
                    sum(discount_amount) as discount_amount,
                    sum(tax_1_amount) as tax_1_amount,
                    sum(tax_2_amount) as tax_2_amount,
                    sum(tax_3_amount) as tax_3_amount,
                    sum(total_tax) as total_tax,
                    sum(total_rate) as total_amount,
                    max(is_complimentary) as is_complimentary,
                    max(is_house_use) as is_house_use
                from `tabReservation Room Rate`
                where
                stay_room_id = '{}'
            """.format(stay.name)

            data = frappe.db.sql(sql,as_dict=1)
    
            if data:
                d = data[0]
                stay.rate =  d["rate"] or 0
                stay.input_rate =  d["input_rate"] or 0
                stay.total_rate =  d["total_amount"] or  0
                stay.adr =  d["adr"]
                stay.discount_amount =d["discount_amount"] or 0
                stay.tax_1_amount =d["tax_1_amount"] or  0
                stay.tax_2_amount =d["tax_2_amount"] or  0
                stay.tax_3_amount =d["tax_3_amount"] or  0
                stay.total_tax =  d["total_tax"] or  0
                
               
        #update is_complimentary
        sql = "select max(is_complimentary) as is_complimentary, max(is_house_use) as is_house_use from `tabReservation Room Rate` where reservation_stay='{}'".format(doc.name)
        complimentary_data = frappe.db.sql(sql, as_dict = 1)
        if len(complimentary_data)>0:
            doc.is_complimentary = complimentary_data[0]["is_complimentary"] 
            doc.is_house_use = complimentary_data[0]["is_house_use"]
        else:
            doc.is_complimentary = 0
            doc.is_house_use = 0

        #update room rate, is_complimentary and house use to room occupy
        data = frappe.db.sql("select rate_type,date,is_complimentary,is_house_use from `tabReservation Room Rate` where reservation_stay='{}' order by date".format(doc.name),as_dict=1)
        
        if len(data)> 0:
            #in room dont have record departure date so we include last record 
            data.append(copy.deepcopy( data[len(data)-1]))
            
            data[len(data)-1]["date"] = add_to_date( data[len(data)-1]["date"] ,days=1)

         
            for r in set([x["rate_type"] for x in data]):
                room_rate = [d for d in data if d["rate_type"] == r][0]
                
                frappe.db.sql("update `tabRoom Occupy` set rate_type=%(rate_type)s, is_complimentary=%(is_complimentary)s, is_house_use=%(is_house_use)s where reservation_stay=%(reservation_stay)s and date in %(dates)s",
                              {
                                  "reservation_stay":doc.name,
                                  "is_complimentary":room_rate["is_complimentary"],
                                  "is_house_use":room_rate["is_house_use"],
                                  "dates":set([y["date"] for y in data if y["rate_type"]==r]),
                                  "rate_type":r
                })
                
                 

        if is_save:
            doc.flags.ignore_on_update= True
            doc.save(  ignore_permissions=True)
            
            frappe.db.commit()

        #delete all invalid room rate record that stay out site of stay date
        frappe.db.sql("delete from `tabReservation Room Rate` where reservation_stay='{}' and date<'{}'".format(doc.name, doc.arrival_date))
        frappe.db.sql("delete from `tabReservation Room Rate` where reservation_stay='{}' and date>='{}'".format(doc.name, doc.departure_date))

        frappe.db.commit()
        return doc


@frappe.whitelist()
def update_city_ledger(name=None,doc=None, run_commit = True):
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
    
    doc.save()
    if run_commit:
        frappe.db.commit()
        
    return doc

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
def get_base_rate(amount,tax_rule,tax_1_rate, tax_2_rate,tax_3_rate):

	t1_r = (tax_1_rate or 0) / 100
	t2_r = (tax_2_rate or 0)  / 100
	t3_r = (tax_3_rate or 0)  / 100
 


	price = 0

	t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1

	t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
	t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


	tax_rate_con = 0


	tax_rate_con = (1 + t1_r + t2_r 
						+ (t1_r * t2_af_add_t1 * t2_r) 
						+ t3_r + (t1_r * t3_af_add_t1 * t3_r) 
						+ (t2_r * t3_af_add_t2 * t3_r)
						+ (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r))


 
	tax_rate_con = tax_rate_con or 0


	price = amount /  tax_rate_con


	return  price

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

def add_room_charge_to_folio(folio,rate,is_night_audit_posing=0):
    rate_type_doc = frappe.get_doc("Rate Type", rate.rate_type)
    doc = {
        "doctype":"Folio Transaction",
        "transaction_type":"Reservation Folio",
        "posting_date":rate.date,
        "transaction_number":folio.name,
        "room_type_id":rate.room_type_id,
        "room_id":rate.room_id,
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
        "valiate_input_amount": False,
        "reservation_room_rate": rate.name,
        "is_night_audit_posing":is_night_audit_posing
    }
    doc = frappe.get_doc(doc)
    doc.flags.ignore_update_reservation = True
    doc.flags.ignore_validate_close_folio = True
    doc.flags.ignore_update_reservation_folio = True
 
    doc.insert()
    return doc
    


def get_master_folio(reservation):
    master_stay = frappe.db.get_list("Reservation Stay", filters={"reservation":reservation, "is_master":"1"})
    if master_stay:
        master_folio = frappe.db.get_list("Reservation Folio", fields=["*"], filters={"reservation_stay":master_stay[0].name, "is_master":1})
        if master_folio:
            return master_folio[0]
    return None

def create_folio(stay):
    doc = frappe.get_doc({
        "doctype":"Reservation Folio",
        "reservation_stay":stay.name,
        "guest":stay.guest
    }).insert()
    return doc




@frappe.whitelist()
def clear_reservation():
    frappe.db.sql("delete from `tabReservation`")
    frappe.db.sql("delete from `tabReservation Stay`")
    frappe.db.sql("delete from `tabReservation Stay Room`")
    frappe.db.sql("delete from `tabReservation Room Rate`")
    frappe.db.sql("delete from `tabTemp Room Occupy`")
    frappe.db.sql("delete from `tabRoom Occupy`")
    frappe.db.sql("delete from `tabFolio Transaction`")
    frappe.db.sql("delete from `tabReservation Folio`")
    frappe.db.sql("update `tabRoom` set housekeeping_status = 'Vacant Clean', reservation_stay='',guest='' , guest_name=''")
    
    frappe.db.sql("delete from `tabSale Product`")
    frappe.db.sql("delete from `tabSale Payment`")
    frappe.db.sql("delete from `tabSale`")
    frappe.db.sql("delete from `tabWorking Day`")
    frappe.db.sql("delete from `tabCashier Shift`")
    frappe.db.sql("delete from `tabRoom Block`")
    frappe.db.sql("delete from `tabDeposit Ledger`")
    frappe.db.sql("delete from `tabDesk Folio`")
    frappe.db.sql("delete from `tabCashier Shift Cash Count`")
    frappe.db.sql("delete from `tabDaily Property Data`")

    frappe.db.sql("delete from `tabComment` where reference_doctype in  ('Reservation','Reservation Stay','Reservation Stay Room','Reservation Room Rate','Temp Room Occupy','Room Occupy','Folio Transaction','Reservation Folio','Sale Product','Sale Payment','Sale','Working Day','Cashier Shift','Frontdesk Note','Room Block')")
    frappe.db.sql("delete from `tabComment` where custom_is_note=1")

    frappe.db.sql("delete from `tabFile` where attached_to_doctype in  ('Reservation','Reservation Stay','Reservation Stay Room','Reservation Room Rate','Temp Room Occupy','Room Occupy','Folio Transaction','Reservation Folio','Sale Product','Sale Payment','Sale','Working Day','Cashier Shift','Frontdesk Note','Room Block')")
    frappe.db.sql("delete from `tabVersion` where ref_doctype in  ('Reservation','Reservation Stay','Reservation Stay Room','Reservation Room Rate','Temp Room Occupy','Room Occupy','Folio Transaction','Reservation Folio','Sale Product','Sale Payment','Sale','Working Day','Cashier Shift','Frontdesk Note','Room Block')")





    room_list = frappe.db.get_all("Room")

    for r in room_list:

        room_doc = frappe.get_doc("Room", r.name)
        room_doc.room_status = "Vacant"
        room_doc.housekeeping_status_code = "Clean"
        
        room_doc.save()
    
    
    frappe.db.commit()

    
    return "done"

@frappe.whitelist()
def get_rate_type_info(name):
    doc = frappe.get_doc("Rate Type", name)
    if not doc.account_code:
        frappe.throw("This account does not have account code")
    
    account_doc =frappe.get_doc("Account Code", doc.account_code)
    tax_rule=None
    if account_doc.tax_rule:
        tax_rule = frappe.get_doc("Tax Rule",account_doc.tax_rule)
    

    if doc.is_house_use==1 or doc.is_complimentary==1:
        tax_rule = None
        
    return {
        "name": name,
        "tax_rule":tax_rule,
        "allow_discount": account_doc.allow_discount,
        "allow_user_to_change_tax": account_doc.allow_user_to_change_tax,
        "allow_user_to_edit_rate": doc.allow_user_to_edit_rate,
        "is_house_use":doc.is_house_use,
        "is_complimentary":doc.is_complimentary
    }



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
def update_reservation_stay_and_reservation(reservation_stay, reservation, reservation_folio=None):
    if reservation_folio:
        update_reservation_folio(name=reservation_folio, doc=None, run_commit=True)
    #check if user pass array
    
    if isinstance(reservation_stay, list):
        for s in list(set(reservation_stay)):
           
            update_reservation_stay ( name=s, doc=None, run_commit=True)
    else:
        update_reservation_stay ( name=reservation_stay, doc=None, run_commit=True)
    
    if isinstance(reservation, list):
        for s in list(set(reservation)):
            update_reservation(name=s, doc=None, run_commit=True)
    else:
        update_reservation(name=reservation, doc=None, run_commit=True)



    
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
        d["comment_by"]:frappe.session.user.full_name

        doc = frappe.get_doc(d).insert(ignore_permissions=True)
        if update_creation_date:
            frappe.db.sql("update `tabComment` set creation=%(creation)s where name=%(name)s",{"name":doc.name, "creation":d["creation"]})
            



def can_change_stay_date(stay_name, arrival,departure):
    #TODO#
    pass



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
            cashier_shift = '{}' and 
            payment_type_group ='Cash' and 
            property='{}'
        """.format(name,property)
    data = frappe.db.sql(sql,as_dict=1)
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
            cashier_shift = '{}' and 
            payment_type <> '' and  
            property='{}'
        group by 
            payment_type_group,
            payment_type
    """.format(name,property)
    summary_by_payment_type = frappe.db.sql(sql, as_dict=1) 

    #payment transaction summary
    sql = """
        select 
            account_code,
            account_name,
            sum(amount * if(type='Debit',1,0)) as total_debit,
            sum(amount * if(type='Debit',0,1)) as total_credit
        from   `tabFolio Transaction`
        where
            cashier_shift = '{}' and 
            ifnull(payment_type,'') <> '' and  
            property='{}'
        group by 
            account_code,
            account_name,
            type
    """.format(name,property)
    payment_transaction_summary = frappe.db.sql(sql, as_dict=1) 
    

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
def get_cash_count_setting():
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
            "exchange_rate":  get_exchange_rate(base_currency, c),
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

def get_exchange_rate(base_currency, second_currency):
    sql = "select exchange_rate from `tabCurrency Exchange` where from_currency='{}' and to_currency = '{}' and docstatus=1 order by posting_date desc, modified desc limit 1"
    data = frappe.db.sql(sql.format(base_currency, second_currency),as_dict=1)
    if len(data)> 0:
        return data[0]["exchange_rate"]
    else:
        return 1
    

def update_is_arrival_date_in_room_rate(stay_name):
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

@frappe.whitelist()
def get_report_config(property,report):
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
            room_doc.save()
            
        frappe.db.commit()

