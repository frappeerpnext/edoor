from edoor.api.cache_functions import get_account_code_sub_account_information, get_master_folio_name_cache
import frappe
from frappe.model.document import bulk_insert
from frappe.model.naming import make_autoname


def create_folio(stay=None, data=None):
    if stay:
        doc = frappe.get_doc({
            "doctype":"Reservation Folio",
            "reservation_stay":stay.name,
            "guest":stay.guest
        }).insert(ignore_permissions=True)
        doc.flags.ignore_validate = True
        doc.flags.ignore_on_update = True
        
        return doc
    else:
        doc = frappe.get_doc(data).insert(ignore_permissions=True)
        doc.flags.ignore_validate = True
        doc.flags.ignore_on_update = True
        return doc
 
def get_master_folio(reservation,create_if_not_exists = False,reopen_folio_if_closed=False):
    master_stay = frappe.db.get_list("Reservation Stay",  filters={"reservation":reservation, "is_master":"1"})
    if master_stay:
        master_folio = frappe.db.get_list("Reservation Folio", filters={"reservation_stay":master_stay[0].name, "is_master":1})
        if master_folio:
            folio_doc = frappe.get_doc("Reservation Folio", master_folio[0].name)
            if reopen_folio_if_closed:
                folio_doc.status="Open"
                folio_doc.flags.ignore_validate = True
                folio_doc.save(ignore_permissions=True)
            return folio_doc
    
    if create_if_not_exists:
        return create_folio(frappe.get_doc("Reservation Stay",master_stay))
    return None

@frappe.whitelist()
def update_reservation_folios(folio_names,run_commit=True):
    if folio_names:
            sql = """
                update `tabReservation Folio` f
                join (
                    select 
                            transaction_number,
                            sum(if(type='Debit',amount,0)) as debit,
                            sum(if(type='Credit',amount,0)) as credit
                        from `tabFolio Transaction` 
                        where
                            transaction_type = 'Reservation Folio' and 
                            transaction_number in %(folio_names)s
                        group by
                            transaction_number
                    ) a 
                on a.transaction_number = f.name
                SET 
                    f.total_credit = a.credit,
                    f.total_debit = a.debit,
                    f.balance = a.debit - a.credit
                    """ 
            frappe.db.sql(sql,{"folio_names":folio_names})
            if run_commit:
                frappe.db.commit()
    
@frappe.whitelist()
def update_reservation_folio(name=None, doc=None,run_commit=True,ignore_validate=False):
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
    doc.flags.ignore_validate = ignore_validate
    doc.save(  ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
        
    return doc

def post_charge_to_folio_afer_check_in(working_day, reservation , stays,master_folio,run_commit = True):
    # get_all stay doc with check in to master
    folio_names = []
    if master_folio:
        folio_names.append(master_folio.name)
        
    stays_info = get_reservation_stay_list_infor(stay_names =[d["stay_name"] for d in stays])
 
    for s in stays_info:
        folio = {}
        if s["paid_by_master_room"] == 1:
            s["reservation_folio"] = master_folio.name
            s["folio_transaction_reservation_stay"] = master_folio.reservation_stay
        else:
            #create stay folio 
            folio = frappe.db.get_list("Reservation Folio",{"reservation_stay":s["name"],"is_master":1})
            
            if len (folio) ==0:
                folio  =create_folio(data={
                    "doctype":"Reservation Folio",
                    "reservation_stay":s["name"],
                    "guest":s["guest"]
                })
                s["reservation_folio"] = folio.name
                s["folio_transaction_reservation_stay"] = folio.reservation_stay
                folio_names.append(folio.name)
        
            else:
                #try to reopen folio if the master folio is close
                folio = frappe.get_doc("Reservation Folio",folio[0].name)
                folio.status="Open"
                folio.flags.ignore_validate = True
                folio.flags.ignore_on_update = True
                folio.save(ignore_permissions=True)
                s["folio_transaction_reservation_stay"] = folio.reservation_stay
                s["reservation_folio"] = folio.name
            
    charge_list = get_charge_list_for_posting_room_charge(stay_names=[d["name"] for d in stays_info], working_day=working_day)
    folio_transaction_list = get_folio_transaction_new_record(stays_infor=stays_info,charge_list=charge_list, working_day = working_day)
    bulk_insert("Folio Transaction",folio_transaction_list , chunk_size=10000)
    
    # update debit, credit and balance to reservation folio 
    update_reservation_folios(folio_names=folio_names ,run_commit=False)
    
    if run_commit:
        frappe.db.commit()
    
          
    # bulk insert here 
    # return folio_transaction_list

def get_charge_list_for_posting_room_charge(stay_names=None,reservation_room_rate_names = None, working_day=None):
    sql="""
        select 
            name, 
            parent_reference,
            reservation_stay,
            reservation,
            parent_reference,
            room_rate_id, 
            account_code, 
            type,
            input_rate,
            price,
            amount ,
            total_amount,
            is_house_use,
            is_complimentary,
            is_package,
            is_package_charge,
            is_package_breakdown,
            adult,
            child,
            quantity,
            room_type_id,
            room_type,
            room_id,
            room_number,
            room_type_alias,
            discount_type,
            discount,
            discount_amount,
            tax_1_rate,
            tax_2_rate,
            tax_3_rate,
            total_tax,
            is_package_charge,
            is_package_breakdown,
            room_rate_id,
            is_base_transaction
        from `tabRevenue Forecast Breakdown`
        where
            date=%(date)s
        """
    if stay_names:
        sql = sql + " and reservation_stay in %(stay_names)s "
    if reservation_room_rate_names:
        sql = sql + " and room_rate_id in %(reservation_room_rate_names)s "
    sql = sql + " order by room_rate_id, sort_order"
     
    return  frappe.db.sql(sql,{"stay_names":stay_names, "reservation_room_rate_names":reservation_room_rate_names,"date":working_day["date_working_day"]},as_dict=1)

def get_folio_transaction_new_record( stays_infor,charge_list,working_day):
    
    
    
    # apploy folio reservation stay to charge list
    for c in charge_list:
        c["folio_transaction_reservation_stay"] = [d for d in stays_infor if d["name"]==c["reservation_stay"]][0]["folio_transaction_reservation_stay"]
    
    folio_transaction_list = []
    
    folio_transaction_list = get_folio_transaction_name([d for d in charge_list if d["parent_reference"] ==""], charge_list)
    
    for t in folio_transaction_list:
        
        stay = [d for d in stays_infor if d["name"]==t.source_reservation_stay][0]
        # read some inforamtion from reservation stay apply to folio transaction
        t.transaction_number = stay["reservation_folio"]
        
        
        t.property= stay["property"]
        t.posting_date = working_day["date_working_day"]
        t.working_day = working_day["name"]
        t.cashier_shift = working_day["cashier_shift"]["name"]
        t.working_date = working_day["date_working_day"]
         
        # guest info
        t.guest = stay["guest"]
        t.guest_name = stay["guest_name"]
        t.guest_type = stay["guest_type"]
        t.nationality= stay["nationality"]
         
        
        # business source and type
        t.business_source = stay["business_source"]
        t.business_source_type = stay["business_source_type"]
        yield t
        

    # return ("x", folio_transaction_list)

 

# recursion fution to get doc with doc name
def get_folio_transaction_name(data,charge_list,parent_doc=None):
    result = []

    for t in data:
        
        doc = frappe.new_doc("Folio Transaction") 
        if not parent_doc:        
            doc.name = make_autoname(doc.naming_series)
        else:
            doc.name  = make_autoname(parent_doc.name + ".-.##")
            doc.parent_reference = parent_doc.name

        doc.transaction_type = "Reservation Folio"
        
        # more doc property heres
        doc.reservation_stay = t["folio_transaction_reservation_stay"]
        doc.source_reservation_stay = t["reservation_stay"]
        doc.reservation= t["reservation"]
        doc.is_auto_post=1
        doc.is_house_use = t["is_house_use"]
        doc.is_complimentary = t["is_complimentary"]
        doc.type=t["type"]
        doc.is_base_transaction = t["is_base_transaction"]
        
        # room inforation
        doc.room_type_id = t["room_type_id"]
        doc.room_type = t["room_type"]
        doc.room_id = t["room_id"]
        doc.room_number = t["room_number"]
        doc.room_type_alias = t["room_type_alias"]
        doc.reservation_room_rate = t["room_rate_id"]
        
        doc.adult = t["adult"]
        doc.child= t["child"]
        doc.quantity=t["quantity"]
        doc.report_quantity=t["quantity"]
        
        doc.is_package = t["is_package"]
        doc.is_package_charge = t["is_package_charge"]
        doc.is_package_breakdown = t["is_package_breakdown"]
        
        
        doc.input_amount = t["input_rate"]
        doc.total_amount = t["total_amount"]
        doc.amount = t["amount"]
        doc.price = t["price"]
        
        
        # # account information
        
        doc.account_code = t["account_code"]
        
        account_info = get_account_code_sub_account_information(doc.account_code)
        doc.account_name =account_info["account_name"]
        doc.account_code_sort_order = account_info["sort_order"]
        doc.allow_enter_quantity = account_info["allow_enter_quantity"]
        doc.report_description = doc.account_name
        doc.flash_report_revenue_group = account_info["flash_report_revenue_group"]
        
        doc.account_category = account_info["account_category"] 
        doc.account_category_sort_order = account_info["account_category_sort_order"] 
        # parent account infor
        doc.parent_account_code =account_info["parent_account_code"]
        doc.parent_account_name = account_info["parent_account_name"]

        doc.account_group = account_info["account_group"]
        doc.account_group_name = account_info["account_group_name"]
        
        # sub account info
        if "discount_account" in account_info:
            doc.discount_account = account_info["discount_account"]
            if doc.discount_account:
                if t["discount_type"] =="Percent":
                    doc.discount_description = "{} - {}%".format( account_info["discount_account_name"], t["discount"] ) #Room Charge Discount - 50.0%
                else:
                    doc.discount_description = account_info["discount_account_name"]
        doc.discount_type = "" if "discount_type" in t else t["discount_type"] 
        doc.discount = "" if "discount" in t else t["discount"] 
        doc.discount_amount= "" if "discount_amount" in t else t["discount_amount"] 
        # tax 1 description
    
        if "tax_1_account" in  account_info:
            doc.tax_1_account = account_info["tax_1_account"]
            if t["tax_1_rate"]>0:
                doc.tax_1_rate = t["tax_1_rate"]
                doc.tax_description  = "{} - {}%".format( account_info["tax_1_description"] , t["tax_rate"])
                
    
        if "tax_2_account" in  account_info:
            doc.tax_2_account = account_info["tax_2_account"]
            doc.tax_2_rate = t["tax_2_rate"]
            if t["tax_2_rate"]>0:
                doc.tax_description  = "{} - {}%".format( account_info["tax_2_description"] , t["tax_1_rate"])
                
    
        if "tax_3_account" in  account_info:
            doc.tax_3_account = account_info["tax_3_account"]
            doc.tax_3_rate = t["tax_3_rate"]
            if t["tax_3_rate"]>0:
                doc.tax_description  = "{} - {}%".format( account_info["tax_3_description"] , t["tax_3_rate"])
                

        doc.total_tax = t["total_tax"] or 0
        
        
  
        # end set doc property

        result.append(doc)
        
        result = result +  get_folio_transaction_name(
                data = [d for d in charge_list if d["parent_reference"]==t["name"]],
                 charge_list=charge_list,
                parent_doc=doc
        )
        

    return result

def get_reservation_stay_list_infor(stay_names):
    sql ="""
        select 
            name,
            reservation,
            is_master,
            paid_by_master_room,
            business_source,
            is_master,
            guest,
            guest_name,
            guest_type,
            nationality,
            property,
            business_source,
            business_source_type
        from `tabReservation Stay`
        where
            name in %(stay_names)s
    """
    return frappe.db.sql(sql,{"stay_names":stay_names},as_dict=1)



def post_charge_to_folio_afer_after_run_night_audit(property, working_day,run_commit=True):
    get_master_folio_name_cache.cache_clear()
    
    folio_names=[]
    # get stay names 
    room_rate_datas = frappe.db.sql("""select 
                                    name,
                                    reservation_stay
                                from `tabReservation Room Rate` 
                                where 
                                    property=%(property)s and 
                                    date=%(date)s and 
                                    is_arrival=0
                                """,{"property":property,"date": working_day["date_working_day"]},as_dict=1) 
    stay_names = list(set([d["reservation_stay"] for d in room_rate_datas]))
    
    if stay_names:
        
        stays_info = get_reservation_stay_list_infor(stay_names =stay_names)
        
        reservation_room_rate_names = [d["name"] for d in room_rate_datas]
        for s in stays_info:
            folio = {}
            if s["paid_by_master_room"] == 1:
                master_folio = get_master_folio_name_cache(s["reservation"])
                s["reservation_folio"] = master_folio.name
                s["folio_transaction_reservation_stay"] = master_folio.reservation_stay
                folio_names.append(master_folio.name)
            else:
                #create stay folio 
                folio = frappe.db.get_list("Reservation Folio",{"reservation_stay":s["name"],"is_master":1})
                
                if len (folio) ==0:
                    folio  =create_folio(data={
                        "doctype":"Reservation Folio",
                        "reservation_stay":s["name"],
                        "guest":s["guest"]
                    })
                    s["reservation_folio"] = folio.name
                    s["folio_transaction_reservation_stay"] = folio.reservation_stay
                    folio_names.append(folio.name)
            
                else:
                    #try to reopen folio if the master folio is close
                    folio = frappe.get_doc("Reservation Folio",folio[0].name)
                    if folio.status=="Closed": 
                        folio.status="Open"
                        folio.flags.ignore_validate = True
                        folio.flags.ignore_on_update = True
                        folio.save(ignore_permissions=True)
                    s["folio_transaction_reservation_stay"] = folio.reservation_stay
                    s["reservation_folio"] = folio.name
            
        charge_list = get_charge_list_for_posting_room_charge(reservation_room_rate_names= reservation_room_rate_names, working_day=working_day)

        folio_transaction_list = get_folio_transaction_new_record(stays_infor=stays_info, charge_list=charge_list , working_day = working_day)
        bulk_insert("Folio Transaction",folio_transaction_list , chunk_size=10000)
        
        # update debit, credit and balance to reservation folio 
        update_reservation_folios(folio_names=folio_names ,run_commit=False)
        
        if run_commit:
            frappe.db.commit()
            
            
