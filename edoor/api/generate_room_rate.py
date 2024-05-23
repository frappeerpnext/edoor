from functools import lru_cache
import json
# from edoor.api.cache_functions import get_account_code_doc, get_rate_type_doc
from edoor.api.cache_functions import get_account_code_doc, get_rate_type_doc, get_tax_rule_doc
from edoor.api.utils import get_date_range,get_reservation_stay_additional_information,get_room_rate
import frappe
import copy
import time
from frappe.utils import getdate
import uuid  
from frappe.model.document import bulk_insert
from edoor.api.tax_calculation import get_tax_breakdown
@frappe.whitelist()
def dome_old():
    from edoor.api.reservation import generate_room_room_rates
    stay_names = frappe.db.sql("select name from `tabReservation Stay` where reservation='RS2024-0751'",as_dict=1)
    
    start_time = time.time()

    # generate_room_room_rates(stay_names = [d["name"] for d in stay_names])
    data = generate_forecast_revenue()
    end_time = time.time()

    duration = end_time - start_time
    return("Duration:", duration, "seconds","xx" )

@frappe.whitelist()
def dome_new():
    
    
    
    start_time = time.time()
   
    # generate_new_room_rate(stay_names=["ST2024-4525"])
    data = generate_forecast_revenue()
    end_time = time.time()

    duration = end_time - start_time
    return("Duration:", duration, "seconds",data)

 
 
def group_change_stay_generate_room_rate(data,run_commit = True): 
    
    stay_names = [d["parent"] for d in data]
    start_date = data[0]["start_date"]
    end_date= data[0]["end_date"]
    generate_rate_type = data[0]["generate_rate_type"]
     
    new_date_ranges = get_date_range(getdate(start_date), getdate(end_date))
    
    # delete room_rate out of range of new date 
    for s in stay_names:
        frappe.db.sql("delete from `tabReservation Room Rate` where not `date` in %(dates)s and reservation_stay=%(stay)s",{"dates":new_date_ranges,"stay":s})
    
    
    # get current stay date list
    sql = "select reservation_stay, date from `tabReservation Room Rate` where reservation_stay in %(reservation_stays)s"
    current_room_rate_data = frappe.db.sql(sql, {"reservation_stays":stay_names},as_dict=1)
    # get stay room info
    stay_rooms_info = get_stays_room_info(stay_names=stay_names)
    reservation_stays = get_reservation_stay_additional_information(stay_names=stay_names)
    new_record_data =  get_new_room_rate_record_for_group_change_stay(
        current_room_rate_data=current_room_rate_data,
        reservation_stays=reservation_stays,
        stay_rooms_info=stay_rooms_info,
        new_date_ranges=new_date_ranges,
        generate_rate_type=generate_rate_type
    )
    bulk_insert("Reservation Room Rate",new_record_data , chunk_size=10000)
    if run_commit:
        frappe.db.commit()    
      

def get_new_room_rate_record_for_group_change_stay(current_room_rate_data, reservation_stays, stay_rooms_info,new_date_ranges,generate_rate_type="stay_rate"):
    for stay in stay_rooms_info:
        dates = get_difference_dates(set([d["date"] for d in current_room_rate_data if d["reservation_stay"] == stay["reservation_stay"] ]),new_dates=set(new_date_ranges))
        stay_info = [d for d in reservation_stays if d["name"] ==stay["reservation_stay"]][0]
        for d in dates:
            if generate_rate_type=="stay_rate":
                new_rate = stay["input_rate"]
            else:
               
                new_rate = get_room_rate(stay_info["property"], stay_info["rate_type"], stay["room_type_id"],stay_info["business_source"],d)	
                
            doc = get_new_rate_doc(
                stay_info= stay_info,
                stay_room_info=stay,
                date= d,
                rate=  new_rate)
            yield doc
    
def get_difference_dates(old_dates, new_dates):
    return new_dates.difference(old_dates)   
    
def get_stays_room_info(stay_names, stay_room_id=""):
    
    sql = """select 
            property, 
            room_type_id,
            room_type,
            room_type_alias, 
            name,
            room_id,
            room_number, 
            parent as reservation_stay, 
            reservation, 
            start_date, 
            end_date,
            adult,
            child,
            pax,
            coalesce(is_manual_rate,0) as is_manual_rate,
            input_rate,
            rate_type
        from `tabReservation Stay Room` 
        where 
            parent in %(stay_names)s 
        """
    if stay_room_id:
        sql = sql + " and name = %(stay_room_id)s"
    data = frappe.db.sql(sql, {"stay_names":stay_names, "stay_room_id":stay_room_id}, as_dict=1)
    return data
 
def generate_new_room_rate(stay_names,run_commit=True):
    get_package_charge_data.cache_clear() 
    # delete old rate if exists 
    frappe.db.sql("delete from `tabReservation Room Rate` where reservation_stay in %(stay_names)s",{"stay_names":stay_names})
    reservation_stays_info =  get_reservation_stay_additional_information(stay_names)
    stay_rooms_info = get_stays_room_info(stay_names)
    
    bulk_insert("Reservation Room Rate",get_new_room_rate_record(reservation_stays_info =reservation_stays_info,stay_rooms_info=stay_rooms_info ) , chunk_size=10000)
    if run_commit:
        frappe.db.commit()


def generate_new_room_rate_by_stay_room_id(reservation_stay, stay_room_id):
    
    
    # delete old rate if exists 
    frappe.db.sql("delete from `tabReservation Room Rate` where stay_room_id  = %(stay_room_id)s",{"stay_room_id":stay_room_id})
    reservation_stays_info =  get_reservation_stay_additional_information([reservation_stay])
    stay_rooms_info = get_stays_room_info([reservation_stay],stay_room_id)
    bulk_insert("Reservation Room Rate",get_new_room_rate_record(reservation_stays_info =reservation_stays_info,stay_rooms_info=stay_rooms_info ) , chunk_size=10000)
    frappe.db.commit()


def get_new_room_rate_record(reservation_stays_info,stay_rooms_info ):
    for stay in stay_rooms_info:
        stay_info = [d for d in reservation_stays_info if d["name"] == stay["reservation_stay"]][0]
        dates = get_date_range(start_date=getdate(stay["start_date"]), end_date=getdate(stay["end_date"]))
        
        for d in dates:
            doc = get_new_rate_doc(stay_info= stay_info, stay_room_info=stay,date= d,rate=stay["input_rate"])
            yield doc
            
        
def get_new_rate_doc(stay_info, stay_room_info, date,rate=0,discount_amount = 0):
    
    doc = frappe.new_doc("Reservation Room Rate")
    doc.name  = str(uuid.uuid4())
    doc.property = stay_room_info["property"]
    doc.reservation = stay_room_info["reservation"]
    doc.reservation_stay = stay_room_info["reservation_stay"]
    doc.reservation_type = stay_info["reservation_type"]
    doc.business_source = stay_info["business_source"]
    doc.business_source_type= stay_info["business_source_type"]
    doc.stay_room_id =  stay_room_info["name"] 
    doc.room_type_id =  stay_room_info["room_type_id"] 
    doc.room_type =  stay_room_info["room_type"] 
    doc.room_type_alias =  stay_room_info["room_type_alias"] 
    doc.room_id =  stay_room_info["room_id"] 
    doc.room_number=  stay_room_info["room_number"] 
    doc.date = date
    
    # guest info
    doc.guest = stay_info["guest"]
    doc.guest_name = stay_info["guest_name"]
    doc.guest_type = stay_info["guest_type"]
    doc.nationality = stay_info["nationality"]
    # rate type info
    doc.rate_type = stay_room_info["rate_type"]
    doc.allow_discount = frappe.db.get_value("Rate Type",doc.rate_type,"allow_discount",cache=True)
    doc.is_package = frappe.db.get_value("Rate Type",doc.rate_type,"is_package",cache=True)
    doc.is_manual_rate=stay_room_info["is_manual_rate"]
    
    # rate culatiation
    doc.input_rate = rate
    # tax calculation
    doc.tax_rule =  stay_info["tax_rule"]
    doc.rate_include_tax =  stay_info["rate_include_tax"] or "No"
    doc.tax_1_rate =  stay_info["tax_1_rate"] or 0
    doc.tax_2_rate =  stay_info["tax_2_rate"] or 0
    doc.tax_3_rate =  stay_info["tax_3_rate"] or 0

    tax_data = get_tax_breakdown(
        tax_rule=doc.tax_rule,
        tax_1_rate=doc.tax_1_rate,
        tax_2_rate=doc.tax_2_rate,
        tax_3_rate=doc.tax_3_rate,
        rate_include_tax=doc.rate_include_tax,
        rate=doc.input_rate,
        discount_amount=discount_amount
    )

    doc.rate = tax_data["rate"]
    doc.tax_rule_data = tax_data["tax_rule_data"]
    doc.tax_1_name = tax_data["tax_1_name"]
    doc.tax_2_name = tax_data["tax_2_name"]
    doc.tax_3_name = tax_data["tax_3_name"]
    doc.tax_1_amount = tax_data["tax_1_amount"]
    doc.tax_2_amount = tax_data["tax_2_amount"]
    doc.tax_3_amount = tax_data["tax_3_amount"]
    doc.taxable_amount_1 = tax_data["taxable_amount_1"]
    doc.taxable_amount_2 = tax_data["taxable_amount_2"]
    doc.taxable_amount_3 = tax_data["taxable_amount_3"]
    doc.total_tax = (doc.tax_1_amount or 0 ) + (doc.tax_2_amount or 0 ) + (doc.tax_3_amount or 0 ) 
    doc.total_rate = (doc.rate or 0) - (doc.discount_amount or 0) + doc.total_tax

    doc.is_active_reservation=1
    doc.is_active= 1
    doc.is_arrival =  1 if getdate(date) == getdate(stay_info["arrival_date"]) else 0 ,
    doc.adult = stay_room_info["adult"]
    doc.child = stay_room_info["child"]
    doc.is_house_use = stay_info["is_house_use"]
    doc.is_complimentary = stay_info["is_complimentary"]
    if doc.is_package==1:
        
        package_data = get_package_charge_data(doc.rate_type)
        
        if package_data:
            if doc.is_arrival:
              
                doc.package_charge_data = json.dumps([d for d in package_data if d["posting_rule"] in ["Everyday","Checked In Date"]])
                
            else:
                doc.package_charge_data = json.dumps([d for d in package_data if d["posting_rule"] in ["Everyday"]])
        
    return doc


@lru_cache(maxsize=128)
def get_package_charge_data(rate_type):
    account_code= frappe.db.get_value("Rate Type", rate_type ,"account_code")
    doc = frappe.get_doc("Account Code",account_code)
    return [{"account_code":d.account_code,"posting_rule":d.posting_rule,"charge_rule":d.charge_rule,"rate":d.rate,"adult_rate":d.adult_rate,"child_rate":d.child_rate} for d in doc.packages]

@frappe.whitelist()
def generate_forecast_revenue(stay_names=None,run_commit=True):
    # clear cache first
    # get_account_code_doc.__wrapped__.cache_clear()
    # get_rate_type_doc.__wrapped__.cache_clear()
    start_time = time.time()

    get_account_code_doc.cache_clear()
    get_rate_type_doc.cache_clear()
    package_base_account_code_charge_breakdown.cache_clear()
    get_tax_rule_doc.cache_clear()
    get_room_rate_account_code_breakdown.cache_clear()
    get_tax_breakdown.cache_clear()

    
    if not stay_names:
        stay_names = [d["name"] for d in frappe.db.sql("select name from `tabReservation Stay` where reservation='RS2024-0858'",as_dict=1)]
     
    sql="delete from `tabRevenue Forecast Breakdown` where reservation_stay in %(stay_names)s"
    sql="delete from `tabRevenue Forecast Breakdown`"

    
    frappe.db.sql(sql,{"stay_names":stay_names})
    sql="""
        select 
            name,
            property,
            date,
            room_type_id,
            room_type,
            room_id,
            room_number,
            rate_type,
            reservation_stay,
            reservation,
            guest,
            input_rate,
            discount_amount,
            tax_1_rate,
            tax_2_rate,
            tax_3_rate,
            adult,
            child,
            tax_rule,
            rate_include_tax,
            is_package,
            package_charge_data
        from `tabReservation Room Rate`
        where 
            reservation_stay in %(stay_names)s
    """
    data = frappe.db.sql(sql,{"stay_names":stay_names},as_dict=1)

    # return data
    new_records =  get_new_revenue_forecast_records(data)
    # return new_records
    bulk_insert("Revenue Forecast Breakdown",new_records , chunk_size=10000)
    if run_commit:
        frappe.db.commit()  
    
    end_time = time.time()

    duration = end_time - start_time
    return("Duration:", duration, "seconds","xx" )
    
def get_new_revenue_forecast_records(room_rate_data):
    for rate in room_rate_data:
        rate_breakdown_param = {
            "rate_type":rate["rate_type"],
            "tax_rule":rate["tax_rule"],
            "rate_include_tax":rate["rate_include_tax"],
            "tax_1_rate":rate["tax_1_rate"],
            "tax_2_rate":rate["tax_2_rate"],
            "tax_3_rate":rate["tax_3_rate"],
            "input_rate":rate["input_rate"],
            "is_package":rate["is_package"],
            "adult":rate["adult"],
            "child":rate["child"],
            "discount_amount":rate["discount_amount"],
            "package_charge_data":rate["package_charge_data"],
        }
        account_code_breakdown = get_room_rate_account_code_breakdown(tuple(sorted(rate_breakdown_param.items())))
 
        account_code_breakdown =[d for d in account_code_breakdown if d["amount"]>0]
       
        for acc in account_code_breakdown:
         
            doc = frappe.new_doc("Revenue Forecast Breakdown")
            doc.name  = str(uuid.uuid4())
            doc.room_rate_id =  rate["name"]
            doc.property = rate["property"]
            doc.guest= rate["guest"]
            doc.room_id= rate["room_id"]
            doc.room_number= rate["room_number"]
            doc.room_type_id= rate["room_type_id"]
            doc.room_type= rate["room_type"]
            doc.room_type= rate["room_type"]
            doc.date= rate["date"]
            doc.reservation= rate["reservation"]
            doc.reservation_stay= rate["reservation_stay"]
            doc.account_code = acc["account_code"]
            doc.type = acc["type"]
            doc.quantity = acc["quantity"]


            # breakdow tax 
            tax_data = get_tax_breakdown( acc["tax_rule"],
                                         rate_include_tax="No" if not acc["rate_include_tax"] else acc["rate_include_tax"], 
                                         tax_1_rate=acc["tax_1_rate"], 
                                         tax_2_rate=acc["tax_2_rate"], 
                                         tax_3_rate=acc["tax_3_rate"],
                                         discount_amount=acc["discount_amount"],
                                         rate=acc["amount"]
                                        )
            doc.amount = tax_data["rate"]

            yield doc

            # discount 
            if "discount_account" in acc and  acc["discount_account"] and acc["discount_amount"]>0:
                
                discount_doc = copy.deepcopy(doc)
                discount_doc.name = str(uuid.uuid4())
                discount_doc.account_code = acc["discount_account"] 
                discount_doc.amount= acc["discount_amount"] 
                discount_doc.type= "Credit" 
                discount_doc.quantity=0 

                yield discount_doc

            if "tax_1_account" in acc and  acc["tax_1_account"] and acc["tax_1_rate"]>0 and tax_data["tax_1_amount"]>0:
                
                tax_1_doc = copy.deepcopy(doc)
                tax_1_doc.name = str(uuid.uuid4())
                tax_1_doc.account_code = acc["tax_1_account"] 
                tax_1_doc.amount= tax_data["tax_1_amount"] 
                tax_1_doc.type= "Debit"
                tax_1_doc.quantity=0
                
                yield tax_1_doc

            if "tax_2_account" in acc and  acc["tax_2_account"] and acc["tax_2_rate"]>0 and tax_data["tax_2_amount"]>0:
                
                tax_2_doc = copy.deepcopy(doc)
                tax_2_doc.name = str(uuid.uuid4())
                tax_2_doc.account_code = acc["tax_2_account"] 
                tax_2_doc.amount= tax_data["tax_2_amount"] 
                tax_2_doc.type= "Debit"
                tax_2_doc.quantity=0
                yield tax_2_doc
                
            if "tax_3_account" in acc and  acc["tax_3_account"] and acc["tax_3_rate"]>0 and tax_data["tax_3_amount"]>0:
                
                tax_3_doc = copy.deepcopy(doc)
                tax_3_doc.name = str(uuid.uuid4())
                tax_3_doc.account_code = acc["tax_3_account"] 
                tax_3_doc.amount= tax_data["tax_3_amount"] 
                tax_3_doc.type= "Debit"
                tax_3_doc.quantity=0
                yield tax_3_doc

      


@lru_cache(maxsize=128)
def get_room_rate_account_code_breakdown(room_rate_data):
    room_rate_data = {key: value for key, value in room_rate_data}
    base_account_codes=[]
    rate_type_doc = get_rate_type_doc(room_rate_data['rate_type'])
    account_code_doc = get_account_code_doc(rate_type_doc.account_code)
    base_code = {"account_code":rate_type_doc.account_code,
                 "allow_discount":account_code_doc.allow_discount,
                "amount":0,
                "tax_1_rate":0,
                "tax_2_rate":0,
                "tax_3_rate":0,
                "discount_amount":0,
                "type":account_code_doc.type,
                "tax_rule":"",
                "quantity":0
            }
    # sub account of main account
    base_code["tax_rule"] = room_rate_data["tax_rule"]
    base_code["rate_include_tax"] = room_rate_data["rate_include_tax"]
    
    if room_rate_data["tax_rule"]:
        tax_rule_doc = get_tax_rule_doc(room_rate_data["tax_rule"])
        
        if tax_rule_doc.tax_1_account and room_rate_data["tax_1_rate"]:
            base_code["tax_1_account"] = tax_rule_doc.tax_1_account
            base_code["tax_1_rate"] = room_rate_data["tax_1_rate"]
        
        if tax_rule_doc.tax_1_account and room_rate_data["tax_2_rate"]:
            base_code["tax_2_account"] = tax_rule_doc.tax_2_account
            base_code["tax_2_rate"] = room_rate_data["tax_2_rate"]
        
        if tax_rule_doc.tax_1_account and room_rate_data["tax_3_rate"]:
            base_code["tax_3_account"] = tax_rule_doc.tax_3_account
            base_code["tax_3_rate"] = room_rate_data["tax_3_rate"]
        
    if account_code_doc.allow_discount and account_code_doc.discount_account:
        base_code["discount_account"]=account_code_doc.discount_account     
    base_account_codes.append(base_code)    
    if room_rate_data["is_package"] ==1:
        package_account_codes =   package_base_account_code_charge_breakdown( tuple(sorted(room_rate_data.items())))
        base_code["amount"] = room_rate_data["input_rate"] - sum([d["amount"] for d in package_account_codes if d["is_package_account"]==1])
        base_account_codes =  base_account_codes + package_account_codes
    else:
         base_code["amount"] = room_rate_data["input_rate"]

    base_code["amount"] = 0 if base_code["amount"]<=0 else base_code["amount"]

    # set discount 
    discountable_amount = room_rate_data["input_rate"] - sum([d["amount"] for d in base_account_codes if d["allow_discount"]==0])
    for a in [d for d in base_account_codes if d["allow_discount"]==1]:
        a["discount"] =  room_rate_data["discount_amount"] /  ( 1 if discountable_amount==0 else  discountable_amount )
        a["discount_amount"] = a["amount"] * a["discount"]
    return base_account_codes

@lru_cache(maxsize=128)
def package_base_account_code_charge_breakdown(room_rate_data):
    room_rate_data = {key: value for key, value in room_rate_data}
    
    data = []
 
    for p in json.loads( room_rate_data["package_charge_data"]):
        account_code_doc = get_account_code_doc(p["account_code"])
        
        doc = {
            "account_code": p["account_code"],
            "allow_discount": account_code_doc.allow_discount,
            "is_package_account": 1,
            "tax_1_rate":0,
            "tax_2_rate":0,
            "tax_3_rate":0,
            "discount_amount":0,
            "tax_rule":"",
            "rate_include_tax": "No",
           "type":account_code_doc.type
        }
        if p["charge_rule"] =="Stay":
            doc["quantity"] = 1
            doc["amount"] = p["rate"]
        elif p["charge_rule"] =="Adult":
            doc["quantity"] = room_rate_data["adult"]
            doc["amount"] = doc["quantity"] * p["adult_rate"] 
        else:
            # child charge rull
            doc["quantity"] = room_rate_data["child"]
            doc["amount"] = doc["quantity"] * p["child_rate"] 
    
    
        if account_code_doc.tax_rule:
            tax_rule_doc = get_tax_rule_doc(account_code_doc.tax_rule)
            doc["tax_rule"] = account_code_doc.tax_rule
            doc["rate_include_tax"] ="Yes" if  tax_rule_doc.is_rate_include_tax else 'No'
            if tax_rule_doc.tax_1_account and   tax_rule_doc.tax_1_rate:
                doc["tax_1_account"] = tax_rule_doc.tax_1_account
                doc["tax_1_rate"] = room_rate_data["tax_1_rate"]
            if tax_rule_doc.tax_2_account and  tax_rule_doc.tax_2_rate :
                doc["tax_2_account"] = tax_rule_doc.tax_2_account
                doc["tax_2_rate"] = room_rate_data["tax_2_rate"]
            if tax_rule_doc.tax_3_account and tax_rule_doc.tax_3_rate:
                doc["tax_3_account"] = tax_rule_doc.tax_3_account
                doc["tax_3_rate"] = room_rate_data["tax_3_rate"]

        if account_code_doc.allow_discount and account_code_doc.discount_account:
           doc["discount_account"]= account_code_doc.discount_account 
           
        data.append(doc) 
    return data  


def get_new_revenue_forecast_doc(room_rate_data, account_code, rate):
    doc = frappe.new_doc("Revenue Forecast Breakdown")
    doc.name  = str(uuid.uuid4())
    doc.room_rate_id = room_rate_data["name"]
    doc.reservation_stay = room_rate_data["reservation_stay"]
    doc.reservation= room_rate_data["reservation"]
    doc.property = room_rate_data["property"]
    doc.guest = room_rate_data["guest"]
    doc.date = room_rate_data["date"]
    doc.room_type_id = room_rate_data["room_type_id"]
    doc.room_type = room_rate_data["room_type"]
    doc.room_id = room_rate_data["room_id"]
    doc.room_number = room_rate_data["room_number"]
    doc.account_code = account_code
    doc.amount = rate
    return doc
 