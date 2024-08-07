# the reason I create this file and not put this code in folio_transaction.py
# because of bad management of global code function
# if put these code below in folio_transaction.py and call some function from generate_room_rate.py 
# it will cause circular error
# will optimize this in the future
from edoor.api.cache_functions import get_account_code_doc, get_account_code_sub_account_information, get_cache_data
from edoor.api.folio_transaction import update_reservation_folio
from edoor.api.generate_room_rate import get_charge_breakdown_by_account_code_breakdown, get_room_rate_account_code_breakdown, package_base_account_code_charge_breakdown
from edoor.api.tax_calculation import get_tax_breakdown
from edoor.api.utils import get_working_day, update_city_ledger, update_deposit_ledger, update_desk_folio, update_payable_ledger
from frappe.model.document import bulk_insert
import frappe
import json
from frappe import _
from frappe.model.naming import make_autoname


@frappe.whitelist()
def dome():
    data = {
        "transaction_type": "Reservation Folio",
        "transaction_number": "FN2024-0019",
        "reservation": "RS2024-0016",
        "reservation_stay": "ST2024-0017",
        "property": "ESTC  & HOTEL's",
        "account_group": "10000",
        "guest": "0001",
        "business_source": "Angkor Daily Tour",
        "is_base_transaction": 1,
        "posting_date": "2024-07-05T17:00:00.000Z",
        "account_code": "10116",
        "tax_rule": "Room Charge Tax",
        "rate_include_tax": "Yes",
        "bank_fee": 0,
        "account_name": "Room Include B/F",
        "type": "Debit",
        "show_print_preview": 0,
        "discount_type": "Percent",
        "discount": 0,
        "target_transaction_type": "",
        "required_select_product": 0,
        "quantity": 10,
        "tax_1_rate": 0,
        "tax_2_rate": 2,
        "tax_3_rate": 10,
        "target_transaction_number": "",
        "input_amount": 10,
        "child": 0,
        "adult": 2
        }
    return get_folio_transaction_calculation(data)

@frappe.whitelist(methods="POST")
def get_folio_transaction_calculation(folio_transaction_data=None):
    data = []
    if not folio_transaction_data:
        folio_transaction_data ={
            "property":"ESTC  & HOTEL's",
            "account_code":"10116",
            "tax_rule": "Room Charge Tax",
            "rate_include_tax": "Yes",
            "tax_1_rate": 0,
            "tax_2_rate": 2,
            "tax_3_rate": 10,
            "input_rate": 20,
            "quantity":5,
            "discount_type": "Percent",
            "discount": 10,
            "adult": 4,
            "child": 1,
            "is_package":0,
            "package_charge_data":'[]'
            }
    
    folio_transaction_data["tax_rule"] ="" if not "tax_rule" in folio_transaction_data else  folio_transaction_data["tax_rule"]
    folio_transaction_data["adult"] =0 if not "adult" in folio_transaction_data else  folio_transaction_data["adult"]
    folio_transaction_data["child"] =0 if not "child" in folio_transaction_data else  folio_transaction_data["child"]
    
    folio_transaction_data["input_rate"] = folio_transaction_data["input_amount"]
    # check if account code is package charge 
    account_doc = get_account_code_doc(folio_transaction_data["account_code"])
    package_data = []
    if account_doc.is_package:
        package_data = [{
            "account_code": d.account_code,
            "posting_rule": d.posting_rule,
            "charge_rule": d.charge_rule,
            "rate": d.rate,
            "adult_rate": d.adult_rate,
            "child_rate": d.child_rate,
            "breakdown_account_code": d.breakdown_account_code or "",
            "discount_breakdown_account_code": d.discount_breakdown_account_code or "",
            "tax_1_breakdown_account_code": d.tax_1_breakdown_account_code or "",
            "tax_2_breakdown_account_code": d.tax_2_breakdown_account_code or "",
            "tax_3_breakdown_account_code": d.tax_3_breakdown_account_code or ""
        } for d in   account_doc.packages]
    folio_transaction_data["is_package"] = account_doc.is_package
    folio_transaction_data["package_charge_data"] = json.dumps(package_data)
    
    
    if "discount_amount" not in folio_transaction_data:
        folio_transaction_data["discount_amount"] = 0
    folio_transaction_data["discount"] = folio_transaction_data["discount"] or 0
 
    account_codes = get_room_rate_account_code_breakdown(json.dumps( folio_transaction_data))
    if folio_transaction_data["discount"]>0:
        if folio_transaction_data["discount_type"]=="Amount":
            discountable_amount = sum(d["amount"] for d in account_codes if d["allow_discount"]==1)
            folio_transaction_data["discount"] = folio_transaction_data["discount"] / (1 if discountable_amount==0 else discountable_amount)

        
        else:
            # convert discount to decimal number 10%=0.1
            folio_transaction_data["discount"] = folio_transaction_data["discount"] / 100
        
        for d in [x for x in account_codes if x["allow_discount"] == 1]:
            d["discount_amount"] = d["amount"] * folio_transaction_data["discount"] 
    # return account_codes
    for acc in account_codes:
        tax_data  =  get_tax_breakdown(
                tax_rule=acc["tax_rule"],
                rate_include_tax=acc["rate_include_tax"], 
                tax_1_rate=acc["tax_1_rate"],
                tax_2_rate=acc["tax_2_rate"], 
                tax_3_rate=acc["tax_3_rate"],
                discount_amount=acc["discount_amount"],
                rate=acc["amount"],
                quantity = acc["quantity"]
        )
        
        if "tax_rule_data" in tax_data:
            del tax_data["tax_rule_data"]
        
        tax_data["account_name"] = acc["account_name"]
        tax_data["tax_1_rate"] = acc["tax_1_rate"]
        tax_data["tax_2_rate"] = acc["tax_2_rate"]
        tax_data["tax_3_rate"] = acc["tax_3_rate"]
        tax_data["rate_include_tax"] = acc["rate_include_tax"]
        tax_data["allow_discount"] = acc["allow_discount"]
        tax_data["discount_amount"] = acc["discount_amount"]
        tax_data["quantity"] = 0 if "quantity" not in acc else  acc["quantity"]
        tax_data["is_package"] = 0 if not "is_package_account" in acc else  acc["is_package_account"]
        data.append(
            tax_data
        )
 
    total_amount = sum(d["total_amount"] for d in data)
    bank_fee =  0
    # bank fee
    if "bank_fee_account"  in folio_transaction_data:
        if "bank_fee" in folio_transaction_data:
            bank_fee = total_amount * (folio_transaction_data["bank_fee"] / 100)
            total_amount = total_amount + bank_fee
    
    return {
        "base_transaction_data": data[0],
        "package_charge_data": [d for d in data if d["is_package"] == 1],
        "discount_amount": sum(d["discount_amount"] for d in data),
        "total_tax": sum(d["total_tax"] for d in data),
        "total_amount": total_amount,
        "bank_fee_amount": bank_fee
    }



@frappe.whitelist(methods="POST")
def create_folio_transaction(data): 
    
    get_cache_data.cache_clear()
    
    if not "input_amount" in data:
        data["input_amount"] = 0
    data["input_rate"] = data["input_amount"]

    # validate here
    # check if folio is not close
    # chekc if reservation is still allow to edit information
    # and more
    working_day = get_working_day(data["property"])
    old_doc = None
    if "name" in data:
        # delete all sub transaction
        # we send old doc to view 
        old_doc = frappe.get_doc("Folio Transaction", data["name"])
        delete_transaction(data["name"])
        
        working_day = {
            "date_working_day":data["working_date"],
            "name":data["working_day"],
            "cashier_shift":{
                "name":data["cashier_shift"]
            }
        }
        
    
    validate_add_folio_transaction(data,working_day)


    # get charge breakdown 
    breakdown_data =  get_folio_transaction_breakdown(data)    
    # frappe.throw(str(breakdown_data))
    
    add_folio_transaction_record(data, breakdown_data,working_day, old_doc)
    
    
    
    # update reservation reservation reservation folio
    
    update_transaction_type_summary(data=data)
    if "reservation_stay" in data:
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"], reservation_stay=[data["reservation_stay"]])
    
    # update creation and ownere when user edit
         
    frappe.db.commit()
        
    if "name" in data:
        frappe.db.sql("update `tabFolio Transaction` set owner='{0}',creation='{1}' where name='{2}' or reference_folio_transaction='{2}'".format(data["owner"],data["creation"],data["name"]))
        frappe.db.commit()

    frappe.msgprint(_("Posting transaction successfully"))
    
    pass

def validate_add_folio_transaction(data,working_day):
    
    if not working_day["cashier_shift"]:
        frappe.throw(_("Please start cashier shift first"))   
 
    
    # check if user select account code
    if not data["account_code"]:
        frappe.throw(_("Please select account code"))
    account_code_doc = get_account_code_doc(data["account_code"])
    if not account_code_doc.allow_zero_amount_posting:
 
        if  data["input_amount"] == 0:
            frappe.throw(_("Please enter amount for {account_name}".format(account_name = account_code_doc.account_name)))
    
    if account_code_doc.allow_enter_quantity:
        quantity = 0 if not "quantity" in data else data["quantity"]
        
        if quantity<=0:
            frappe.throw(_("Please enter quantity"))
        
    if account_code_doc.required_select_product :
        if not "product" in data or not data["product"]:
            frappe.throw(_("Please select product for this account {account_code} - {account_name}".format( account_code =  account_code_doc.name, account_name = account_code_doc.account_name)))
    
    
    # validate if folio transaction parent transaction is not close
    parent_doc_status = frappe.db.get_value(data["transaction_type"],data["transaction_number"],"status")
    if parent_doc_status=="Closed":
         frappe.throw(_("{transaction_type} number {transaction_number} is already closed.".format(transaction_type=data["transaction_type"],transaction_number=data["transaction_number"])))
         
    
    if "reservation_stay" in data:
        reservation_status =  frappe.db.get_value("Reservation Stay", data["reservation_stay"],"reservation_status")
        allow_edit_information = frappe.db.get_value("Reservation Status",reservation_status,"allow_user_to_edit_information")
        if not allow_edit_information:
            frappe.throw(_("This reservation stay {reservaiton_stay} with status {status} is not allow to edit information".format(reservaiton_stay = data["reservation_stay"], status =reservation_status)))
    
@frappe.whitelist()
def get_folio_transaction_breakdown(data=None):
    
    if not  data:
        data = {
            "transaction_type": "Reservation Folio",
            "transaction_number": "FN2024-1137",
            "reservation": "RS2024-1257",
            "reservation_stay": "ST2024-7059",
            "property": "ESTC  & HOTEL's",
            "account_group": "10000",
            "guest": "0003",
            "business_source": "Angkor Daily Tour",
            "is_base_transaction": 1,
            "posting_date": "2024-06-30",
            "account_code": "10116",
            "tax_rule": "Room Charge Tax",
            "rate_include_tax": "Yes",
            "bank_fee": 0,
            "account_name": "Room Include B/F",
            "type": "Debit",
            "show_print_preview": 0,
            "discount_type": "Percent",
            "discount": 10,
            "discount_amount":0,
            "target_transaction_type": "",
            "required_select_product": 0,
            "quantity": 10,
            "tax_1_rate": 0,
            "tax_2_rate": 2,
            "tax_3_rate": 10,
            "target_transaction_number": "",
            "taxable_amount_2": 89.126559714795,
            "taxable_amount_1": 89.126559714795,
            "taxable_amount_3": 90.90909090909089,
            "input_amount":100,
            "adult": 2,
            "child": 1
            }
    data["adult"] = 0 if not "adult" in data else data["adult"]
    data["child"] = 0 if not "child" in data else data["child"]
    data["tax_rule"] = "" if not "tax_rule" in data else data["tax_rule"]
    data["quantity"] = 1 if not "quantity" in data else data["quantity"]
    if data["quantity"]<=0:
        data["quantity"] = 1
        
    
    account_doc = get_account_code_doc(data["account_code"])

        
    package_data = []
    if account_doc.is_package:
        package_data = [{
            "account_code": d.account_code,
            "posting_rule": d.posting_rule,
            "charge_rule": d.charge_rule,
            "rate": d.rate,
            "adult_rate": d.adult_rate,
            "child_rate": d.child_rate,
            "breakdown_account_code": d.breakdown_account_code or "",
            "discount_breakdown_account_code": d.discount_breakdown_account_code or "",
            "tax_1_breakdown_account_code": d.tax_1_breakdown_account_code or "",
            "tax_2_breakdown_account_code": d.tax_2_breakdown_account_code or "",
            "tax_3_breakdown_account_code": d.tax_3_breakdown_account_code or ""
        } for d in   account_doc.packages]
    

    # I am here 
    rate_breakdown_param = {
            "tax_rule":data["tax_rule"],
            "rate_include_tax":data["rate_include_tax"],
            "tax_1_rate": 0 if not "tax_1_rate" in data else  data["tax_1_rate"],
            "tax_2_rate":0 if not "tax_2_rate" in data else data["tax_2_rate"],
            "tax_3_rate":0 if not "tax_3_rate" in data else data["tax_3_rate"],
            "input_rate":data["input_amount"],
            "is_package":account_doc.is_package,
            "adult":data["adult"],
            "child": data["child"],
            "discount":0 if not "discount" in data else  data["discount"],
            "discount_amount":0 if not "discount_amount" in data else  data["discount_amount"],
            "package_charge_data":json.dumps( package_data),
            "quantity":data["quantity"]
        }
    # we send account account_doc to function because we want to save db connect 
    # for get account code data in function get_room_rate_account_code_breakdown
    # and in funtion get_room_rate_account_code_breakdown get account doc is from rate type
    # but here we dont have rate type that why we send account_code doc here
    
    rate_breakdown_param["account_code"] = data["account_code"]
    get_room_rate_account_code_breakdown.cache_clear()
    get_charge_breakdown_by_account_code_breakdown.cache_clear()
    # package_base_account_code_charge_breakdown.cache_clear()
    
    account_code_breakdown = get_room_rate_account_code_breakdown(json.dumps(rate_breakdown_param))
   
    account_code_breakdown =[d for d in account_code_breakdown if d["amount"]>0 or d["is_package_account"]==0]
    account_code_breakdown = get_charge_breakdown_by_account_code_breakdown(json.dumps(account_code_breakdown)) 

    return account_code_breakdown

def add_folio_transaction_record(data, breakdown_data,working_day,old_doc=None):

    if "base_account" in breakdown_data:
        base_doc = get_folio_transaction_doc_share_property(data, breakdown_data["base_account"],working_day)
        if "name" in data:
            base_doc.flags.doc_name =data["name"]
            base_doc.flags.old_doc = old_doc
        # frappe.throw(base_doc.name)
        base_doc.is_base_transaction = 1
        base_doc.input_amount = breakdown_data["base_account"]["input_rate"]
        base_doc.amount = breakdown_data["base_account"]["amount"]
        base_doc.transaction_amount = breakdown_data["base_account"]["transaction_amount"]
        base_doc.discount_amount = breakdown_data["base_account"]["discount_amount"]
        base_doc.total_tax = breakdown_data["base_account"]["total_tax"]
        

        
        base_doc.price =    base_doc.amount if base_doc.quantity ==0 else base_doc.amount / base_doc.quantity
        base_doc.total_amount = base_doc.amount - (base_doc.discount_amount or  0)+ (base_doc.total_tax or 0)
        
        if base_doc.discount_type=="Percent":
            if base_doc.discount>100:
                frappe.throw(_("Discount  percent must be less than or equal to 100"))
        else:
            if base_doc.discount>0 and base_doc.discount> base_doc.input_amount:
                frappe.throw(_("Discount amount must be less than or equal to amount"))

        
        if "package_accounts" in breakdown_data:
            base_doc.total_sub_package_charge  = sum([d["amount"] - ( d["discount_amount"] or  0)+ (d["total_tax"] or 0)  for d in breakdown_data["package_accounts"]]) 
        
        # bank fee
        if "bank_fee_account"  in data:
            if "bank_fee" in data:
                base_doc.bank_fee_amount = base_doc.total_amount * (data["bank_fee"] / 100)
                base_doc.amount = base_doc.amount +  base_doc.bank_fee_amount 
                base_doc.total_amount = base_doc.total_amount + base_doc.bank_fee_amount 
                base_doc.transaction_amount = base_doc.transaction_amount + base_doc.bank_fee_amount
        update_folio_transaction_note(base_doc)

        base_doc.insert()
    
 
        # add bank fee account
        if base_doc.bank_fee_account:
            if base_doc.bank_fee:
                doc = get_folio_transaction_doc_share_property(data,{"account_code": base_doc.bank_fee_account, "amount":base_doc.bank_fee_amount},working_day)
                doc.input_amount =base_doc.bank_fee_amount
                doc.is_base_transaction = 1
                doc.amount =base_doc.bank_fee_amount
                doc.price =  base_doc.bank_fee_amount
                doc.total_amount =base_doc.bank_fee_amount
                doc.transaction_amount =base_doc.bank_fee_amount
                doc.reference_number = base_doc.name  
                doc.bank_fee_account = ""
                doc.bank_fee_amount = 0
                doc.bank_fee = 0
                doc.reference_folio_transaction = base_doc.name
                doc.note = _("Credit card processing fee")
                doc.report_description = "Bank Fee {bank_fee}% of {amount}".format(bank_fee=base_doc.bank_fee, amount= frappe.format_value(base_doc.input_amount,"Currency"))
                doc.is_auto_post =1
                doc.insert(ignore_permissions=True)

        
        
        # base account sub account
        for s in  breakdown_data["base_account"]["sub_account"]:
            sub_doc = get_folio_transaction_doc_share_property(data, s,working_day)
            sub_doc.naming_series = base_doc.name + ".-.##"
            sub_doc.is_base_transaction = 0
            sub_doc.parent_reference = base_doc.name
            sub_doc.input_amount = s["amount"]
            sub_doc.amount = sub_doc.input_amount
            sub_doc.quantity= 0
            sub_doc.report_quantity= 0
            sub_doc.price =    sub_doc.input_amount
            sub_doc.total_amount =  sub_doc.input_amount
            sub_doc.transaction_amount =  sub_doc.input_amount
            sub_doc.reference_folio_transaction = base_doc.name
            sub_doc.flags.ignore_post_audit_trail = True
            sub_doc.product = ""
            sub_doc.product_name = ""
            sub_doc.unit= ""
            sub_doc.insert(ignore_permissions=True)
    # breakdown account
    if "breakdown_accounts" in breakdown_data:
        for b in breakdown_data["breakdown_accounts"]:
            doc = get_folio_transaction_doc_share_property(data, b,working_day)
            doc.naming_series = base_doc.name + ".-.##"
            doc.reference_folio_transaction = base_doc.name
            doc.parent_reference = base_doc.name
            doc.is_base_transaction = 0
            doc.is_package_breakdown = 1
            doc.input_amount = b["amount"]
            doc.transaction_amount = b["amount"]
            doc.quantity = 0
            doc.report_quantity = 0
            doc.amount = b["amount"]
            doc.price = doc.amount
            doc.total_amount = doc.amount
            doc.insert(ignore_permissions=True)

            
            # base account sub account
            for s in  b["sub_account"]:
                sub_doc = get_folio_transaction_doc_share_property(data, s,working_day)
                sub_doc.naming_series = doc.name + ".-.##"
                sub_doc.reference_folio_transaction = base_doc.name
                sub_doc.is_base_transaction = 0
                sub_doc.is_package_breakdown = 1
                sub_doc.parent_reference = doc.name
                sub_doc.input_amount = s["amount"]
                sub_doc.amount = sub_doc.input_amount
                sub_doc.price =    sub_doc.input_amount
                sub_doc.total_amount =  sub_doc.input_amount
                sub_doc.transaction_amount =  sub_doc.input_amount
                sub_doc.quantity = 0
                sub_doc.report_quantity = 0
                sub_doc.flags.ignore_post_audit_trail = True
                sub_doc.insert(ignore_permissions=True)
            
    # package account
    if "package_accounts" in breakdown_data:
        for p in breakdown_data["package_accounts"]:
            doc = get_folio_transaction_doc_share_property(data, p ,working_day)
            doc.naming_series = base_doc.name + ".-.##"
            doc.reference_folio_transaction = base_doc.name
            doc.is_base_transaction = 1
            doc.is_package_charge = 1
            doc.parent_reference = base_doc.name
            doc.input_amount = p["input_rate"]
            doc.amount = p["amount"]
            
            doc.discount_amount = p["discount_amount"]
            doc.total_tax = p["total_tax"]
            
            doc.quantity= p["quantity"]
            doc.report_quantity= p["quantity"]
            doc.price =    doc.amount if doc.quantity ==0 else doc.amount / doc.quantity
            doc.total_amount = doc.amount - (doc.discount_amount or  0)+ (doc.total_tax or 0)
            doc.transaction_amount =  p["transaction_amount"]
            doc.flags.ignore_post_audit_trail = True
            doc.insert(ignore_permissions=True)
            
            # base account sub account
            for s in  p["sub_account"]:
                sub_doc = get_folio_transaction_doc_share_property(data, s,working_day)
                sub_doc.naming_series = doc.name + ".-.##"
                sub_doc.reference_folio_transaction = base_doc.name
                sub_doc.is_base_transaction = 0
                sub_doc.is_package_charge = 1
                sub_doc.parent_reference = doc.name
                sub_doc.input_amount = s["amount"]
                sub_doc.amount = sub_doc.input_amount
                sub_doc.price =    sub_doc.input_amount
                sub_doc.total_amount =  sub_doc.input_amount
                sub_doc.transaction_amount =  sub_doc.input_amount
                sub_doc.flags.ignore_post_audit_trail = True
                sub_doc.insert(ignore_permissions=True)
                
    # if system transfer account
 
    if base_doc.target_transaction_type and  base_doc.target_transaction_number:
        doc = get_folio_transaction_doc_share_property(data,{"account_code": base_doc.target_account_code},working_day)
        doc.reference_number = base_doc.name  
        doc.reference_folio_transaction = base_doc.name
        doc.source_transaction_number= base_doc.transaction_number
        doc.source_transaction_type = base_doc.transaction_type
        doc.transaction_type =  base_doc.target_transaction_type
        doc.transaction_number  = base_doc.target_transaction_number
        
        # assign reservation, stay, source, room, room type
        if data["target_transaction_type"] =="Reservation Folio":
            target_doc = frappe.get_doc("Reservation Folio",data["target_transaction_number"])
            doc.reservation = target_doc.reservation
            doc.reservation_stay = target_doc.reservation_stay
            doc.reservation_status = target_doc.reservation_status
            doc.reservation_status_color = target_doc.reservation_status_color
            doc.reservation_type = frappe.db.get_value("Reservation", target_doc.reservation, "reservation_type")
            doc.guest = target_doc.guest
            doc.guest_name = frappe.get_cached_value("Customer", target_doc.guest,"customer_name_en")
            doc.phone_number = frappe.get_cached_value("Customer", target_doc.guest,"phone_number")
            doc.email = frappe.get_cached_value("Customer", target_doc.guest,"email_address")
            
            doc.business_source = target_doc.business_source
            doc.business_source_type = frappe.get_cached_value("Business Source",target_doc.business_source,"business_source_type")
            doc.room_id =""
            update_room_information(doc)
            
        elif    data["target_transaction_type"] =="City Ledger":
            
            if not base_doc.reservation_stay:
                doc.reservation =""
                doc.reservation_stay = ""
                doc.reservation_status = ""
                doc.reservation_status_color =""
                doc.reservation_type = ""
            if not base_doc.guest:
                doc.guest = ""
                doc.guest_name = ""
                doc.phone_number = ""
                doc.email = ""
            if not base_doc.room_id:
                doc.room_id= ""
                doc.room_number= ""
                doc.room_type= ""
                doc.room_type_alias= ""
            
        doc.is_base_transaction = 1
        doc.input_amount = base_doc.input_amount
        doc.amount =  base_doc.input_amount
        doc.price =     base_doc.input_amount
        doc.total_amount =  base_doc.input_amount
        doc.transaction_amount =  base_doc.input_amount
        doc.is_auto_post = 1
        # clear target transfer info from share property
        doc.target_transaction_type  =""
        doc.target_transaction_number  =""
        doc.target_account_code  =""
        doc.target_account_type  =""
        
       
        # prepare note
        update_folio_transaction_note(doc,base_doc=base_doc)
        doc.insert(ignore_permissions=True)
        update_transaction_type_summary({
            "transaction_type":base_doc.target_transaction_type,
            "transaction_number":base_doc.target_transaction_number
        })

        
def get_folio_transaction_doc_share_property(data,folio_transaction_data,working_day):
    doc = frappe.new_doc("Folio Transaction")
    # dynamic set property from input form
    for key, value in data.items():
        setattr(doc, key, value)

    
    
    doc.working_day = working_day["name"]
    doc.working_date = working_day["date_working_day"]
    doc.cashier_shift = working_day["cashier_shift"]["name"]
     
    # guest info
    # get cache data for guest

    if doc.guest:
        guest_data = get_cache_data("Customer",data["guest"],"customer_name_en,customer_group,country")
        doc.guest_name = guest_data["customer_name_en"]
        doc.guest_type = guest_data["customer_group"]
        doc.nationality = guest_data["country"]

    account_info = get_account_code_sub_account_information(folio_transaction_data["account_code"])
    doc.account_code = folio_transaction_data["account_code"]
    
    
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
    doc.tax_rule = account_info["tax_rule"]
    
    if doc.allow_enter_quantity == 0:
        doc.quantity = 0
    if account_info["show_quantity_in_report"]==1:
        doc.report_quantity = doc.quantity or 1
   
    
    
    doc.is_package = account_info["is_package"]
        
    # more doc property heres
    if doc.reservation_stay:
        doc.source_reservation_stay = doc.source_reservation_stay or doc.reservation_stay
        # get reservation data  to update to folio transaction such as reservation type, reservation status, ....
        stay_info = get_cache_data("Reservation Stay",doc.reservation_stay,"reservation_type,business_source,business_source_type,reservation_status,status_color")
        doc.reservation_status = stay_info["reservation_status"]
        doc.reservation_status_color= stay_info["status_color"]
        doc.reservation_type = stay_info["reservation_type"]
        doc.business_source = stay_info["business_source"]
        doc.business_source_type = stay_info["business_source_type"]
 
    
    doc.type = account_info["type"]

    # room info
    update_room_information(doc)

    if doc.target_transaction_type and doc.target_transaction_number:
        doc.city_ledger_name = frappe.get_cached_value("City Ledger",doc.target_transaction_number,"city_ledger_name")
        doc.city_ledger_type = frappe.get_cached_value("City Ledger",doc.target_transaction_number,"city_ledger_type")
    
    # # sub account info
    if "discount_account" in account_info:
        doc.discount_account = account_info["discount_account"]
        if doc.discount_account:
            if data["discount_type"] =="Percent":
                doc.discount_description = "{} - {}%".format( account_info["discount_account_name"], data["discount"] ) #Room Charge Discount - 50.0%
            else:
                doc.discount_description = account_info["discount_account_name"]
            doc.discount_type = "Percent" if not "discount_type"  in data  else data["discount_type"] 
          
    # # tax 1 description
    if "tax_1_account" in  account_info and "tax_1_rate" in folio_transaction_data:
        doc.tax_1_account = account_info["tax_1_account"]
        # frappe.throw(str(folio_transaction_data))
        if folio_transaction_data["tax_1_rate"]>0:
            doc.tax_1_rate = folio_transaction_data["tax_1_rate"]
            doc.tax_1_description  = "{} - {}%".format( account_info["tax_1_description"] , folio_transaction_data["tax_1_rate"])
            

    if "tax_2_account" in  account_info and "tax_2_rate" in folio_transaction_data:
        doc.tax_2_account = account_info["tax_2_account"]
        doc.tax_2_rate = folio_transaction_data["tax_2_rate"]
        if folio_transaction_data["tax_2_rate"]>0:
            doc.tax_2_description  = "{} - {}%".format( account_info["tax_2_description"] , folio_transaction_data["tax_2_rate"])
            

    if "tax_3_account" in  account_info  and "tax_3_rate" in folio_transaction_data:
        doc.tax_3_account = account_info["tax_3_account"]
        doc.tax_3_rate = folio_transaction_data["tax_3_rate"]
        if folio_transaction_data["tax_3_rate"]>0:
            doc.tax_3_description  = "{} - {}%".format( account_info["tax_3_description"] , folio_transaction_data["tax_3_rate"])
            
    if "total_tax" in folio_transaction_data:
        doc.total_tax = folio_transaction_data["total_tax"] or 0   
    
   
      
    return doc

def update_room_information(doc):
    if not doc.room_id:
        room_info = frappe.db.sql( "select room_id,room_number,room_type,room_type_id, room_type_alias from `tabRoom Occupy` where reservation_stay=%(reservation_stay)s and property=%(property)s and date=%(date)s limit 1",{"property":doc.property,"reservation_stay":doc.reservation_stay,"date": doc.posting_date},as_dict=1)
        if room_info:
            room_info = room_info[0]
            doc.room_id = room_info["room_id"]
            doc.room_number = room_info["room_number"]
            doc.room_type_id = room_info["room_type_id"]
            doc.room_type = room_info["room_type"]
            doc.room_type_alias = room_info["room_type_alias"]
        else:
            # get froom from `tabReservation Room`
            room_info = frappe.db.sql( "select room_id,room_number,room_type,room_type_id, room_type_alias from `tabReservation Stay Room` where parent=%(reservation_stay)s and property=%(property)s  limit 1",{"property":doc.property,"reservation_stay":doc.reservation_stay},as_dict=1)
            if room_info:
                room_info = room_info[0]
                doc.room_id = room_info["room_id"]
                doc.room_number = room_info["room_number"]
                doc.room_type_id = room_info["room_type_id"]
                doc.room_type = room_info["room_type"]
                doc.room_type_alias = room_info["room_type_alias"]
    else:
        doc.room_number , doc.room_type_id, doc.room_type , doc.room_type_alias = frappe.db.get_value("Room",doc.room_id,["room_number","room_type_id","room_type","room_type_alias"])


def update_folio_transaction_note(doc,base_doc=None):
    if doc.target_transaction_type and  doc.target_transaction_number:
        if doc.note:
            doc.note = doc.note + "\n"
        if doc.target_transaction_type =="Reservation Folio":
            room_number = frappe.db.get_value("Reservation Folio", doc.target_transaction_number, "rooms")
            doc.note = (doc.note or "") + _("Folio balance transfer to folio # {folio_number}, room: {room_number} ".format(folio_number = doc.target_transaction_number, room_number=room_number))
        elif doc.target_transaction_type =="City Ledger":
            doc.note = (doc.note or "") + _("City Ledger Transfer to {city_ledger} - {city_ledger_name}".format(city_ledger = doc.target_transaction_number, city_ledger_name=doc.city_ledger_name))
            
    elif doc.source_transaction_type and  doc.source_transaction_number:
        if doc.note:
            doc.note = doc.note + "\n"
        doc.note = (doc.note or "") + _("Transfer from {source_transaction_type} #: {source_transaction_number}, Room: {room_number}".format(transaction_type=doc.transaction_type, source_transaction_type = doc.source_transaction_type,source_transaction_number=doc.source_transaction_number, reference_folio_transaction = doc.reference_folio_transaction,room_number=base_doc.room_number))
        

def update_transaction_type_summary(data):
    
    if data["transaction_type"]=='Reservation Folio':
        update_reservation_folio(name= data["transaction_number"], run_commit=False, ignore_validate=True)

    elif data["transaction_type"]=='Deposit Ledger':
        update_deposit_ledger( name=  ["transaction_number"], run_commit=False, ignore_validate=True, ignore_on_update=True )
    elif data["transaction_type"]=='Desk Folio':
        update_desk_folio(name=data["transaction_number"], ignore_on_update=True, ignore_validation= True , run_commit= False)	
    elif data["transaction_type"]=='Payable Ledger':
        update_payable_ledger(name= data["transaction_number"],run_commit=False, ignore_on_update= True, ignore_validate= True )    
    elif data["transaction_type"]=='City Ledger':
    
        update_city_ledger(name= data["transaction_number"],run_commit=False, ignore_on_update= True, ignore_validate= True )    
        
        
def delete_transaction(parent_transaction_name):
    frappe.db.sql("delete from `tabFolio Transaction` where reference_folio_transaction='{0}' or name='{0}'".format(parent_transaction_name))
    # update tab series
    frappe.db.sql("select * from `tabSeries` where name like '{}-%'".format(parent_transaction_name))