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
 
  
 
def group_change_stay_generate_room_rate(data,run_commit = True): 
    get_room_rate_breakdown.cache_clear()
    get_package_charge_data.cache_clear()
    stay_names = [d["parent"] for d in data]
    start_date = data[0]["start_date"]
    end_date= data[0]["end_date"]
    generate_rate_type = data[0]["generate_rate_type"]
     
    new_date_ranges = get_date_range(getdate(start_date), getdate(end_date))
    
    # delete room_rate out of range of new date 
    for s in stay_names:
        frappe.db.sql("delete from `tabReservation Room Rate` where not `date` in %(dates)s and reservation_stay=%(stay)s",{"dates":new_date_ranges,"stay":s})
    
    
    # get current stay date list
    sql = "select reservation_stay, date,input_rate from `tabReservation Room Rate` where reservation_stay in %(reservation_stays)s order by date"
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
                if current_room_rate_data:
                    # check if date < current stay rate then get rate from fist night stay rate
                    # else get last rate from last stay rate
            
                    if getdate(d)<=current_room_rate_data[0]["date"]:
                        new_rate = current_room_rate_data[0]["input_rate"]
                    else:
                        new_rate = current_room_rate_data[len(current_room_rate_data)-1]["input_rate"]
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


def get_first_stay_rate():
    pass
 
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
    get_room_rate_breakdown.cache_clear()
    get_tax_breakdown.cache_clear()
    get_rate_type_doc.cache_clear()
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
    rate_type_doc = get_rate_type_doc(doc.rate_type)
    doc.allow_discount = rate_type_doc.allow_discount
    doc.is_package = rate_type_doc.is_package
    
    doc.is_manual_rate=stay_room_info["is_manual_rate"]
    
    # rate culatiation
    doc.input_rate = rate
    # tax calculation
    doc.tax_rule =  stay_info["tax_rule"]
    doc.rate_include_tax =  stay_info["rate_include_tax"] or "No"
    doc.tax_1_rate =  stay_info["tax_1_rate"] or 0
    doc.tax_2_rate =  stay_info["tax_2_rate"] or 0
    doc.tax_3_rate =  stay_info["tax_3_rate"] or 0
    
    

    doc.is_active_reservation=1
    doc.is_active= 1
    
    doc.is_arrival =  1 if getdate(date) == getdate(stay_info["arrival_date"]) else 0
    doc.adult = stay_room_info["adult"]
    doc.child = stay_room_info["child"]
    doc.is_house_use = stay_info["is_house_use"]
    doc.is_complimentary = stay_info["is_complimentary"]
    doc.is_breakfast_include = rate_type_doc.is_breakfast_include
    
    if doc.is_package==1:
        
        package_data = get_package_charge_data(doc.rate_type)
        
        if package_data:
            if doc.is_arrival:
              
                doc.package_charge_data = json.dumps([d for d in package_data if d["posting_rule"] in ["Everyday","Checked In Date"]])
                
            else:
                doc.package_charge_data = json.dumps([d for d in package_data if d["posting_rule"] in ["Everyday"]])

    rate_breakdown = get_room_rate_breakdown(json.dumps({
        "rate_type":doc.rate_type,
        "tax_rule":doc.tax_rule,
        "rate_include_tax":doc.rate_include_tax,
        "tax_1_rate":doc.tax_1_rate,
        "tax_2_rate":doc.tax_2_rate,
        "tax_3_rate":doc.tax_3_rate,
        "input_rate":doc.input_rate,
        "is_package":doc.is_package,
        "discount_type":doc.discount_type,
        "discount":doc.discount or 0,
        "discount_amount":doc.discount_amount or 0,
        "adult":doc.adult,
        "child":doc.child,
        "package_charge_data":doc.package_charge_data
    }))
    

    doc.tax_rule_data = rate_breakdown["tax_rule_data"]
    doc.total_tax =rate_breakdown["total_tax"]
    doc.total_room_charge = rate_breakdown["total_room_charge"]
    doc.total_other_charge = rate_breakdown["total_other_charge"]
    doc.total_rate = rate_breakdown["total_amount"]
    doc.discount_amount= rate_breakdown["discount_amount"]
    
    if doc.tax_rule_data:
        tax_info = json.loads(doc.tax_rule_data)
        if tax_info:
            doc.tax_1_name = tax_info["tax_1_name"] 
            doc.tax_2_name = tax_info["tax_2_name"] 
            doc.tax_3_name = tax_info["tax_3_name"] 
 
    return doc


@lru_cache(maxsize=128)
def get_package_charge_data(rate_type):
    account_code= frappe.db.get_value("Rate Type", rate_type ,"account_code")
    doc = frappe.get_doc("Account Code",account_code)
    return [{
                "account_code":d.account_code,
                "posting_rule":d.posting_rule,
                "charge_rule":d.charge_rule,
                "rate":d.rate,
                "adult_rate":d.adult_rate,
                "child_rate":d.child_rate,
                "breakdown_account_code": d.breakdown_account_code,
                "discount_breakdown_account_code": d.discount_breakdown_account_code or "",
                "tax_1_breakdown_account_code": d.tax_1_breakdown_account_code or "",
                "tax_2_breakdown_account_code": d.tax_2_breakdown_account_code or "",
                "tax_3_breakdown_account_code": d.tax_3_breakdown_account_code or "",
             } for d in doc.packages]

@frappe.whitelist()
def test_me():
    return get_room_rate_breakdown(json.dumps( {"rate_type": 
        "Rate Include B/F",
        "tax_rule": "Room Charge Tax",
        "rate_include_tax": "Yes",
        "tax_1_rate": 0,
        "tax_2_rate": 2.0,
        "tax_3_rate": 10.0,
        "input_rate": 300.0,
        "is_package": 1,
        "discount_type": "Percent",
        "discount": 0,
        "discount_amount": 0,
        "adult": 1,
        "child": 0,
        "package_charge_data": '[{\"account_code\": \"10837\", \"posting_rule\": \"Everyday\", \"charge_rule\": \"Adult\", \"rate\": 0.0, \"adult_rate\": 6.0, \"child_rate\": 0.0, \"breakdown_account_code\": \"10119\", \"discount_breakdown_account_code\": \"40103\", \"tax_1_breakdown_account_code\": \"\", \"tax_2_breakdown_account_code\": \"\", \"tax_3_breakdown_account_code\": \"20107\"}, {\"account_code\": \"10838\", \"posting_rule\": \"Everyday\", \"charge_rule\": \"Child\", \"rate\": 0.0, \"adult_rate\": 0.0, \"child_rate\": 3.0, \"breakdown_account_code\": \"10119\", \"discount_breakdown_account_code\": \"40103\", \"tax_1_breakdown_account_code\": \"\", \"tax_2_breakdown_account_code\": \"\", \"tax_3_breakdown_account_code\": \"20107\"}]'}))

@frappe.whitelist()
def dome():
    data = [{'name': '2687a155-32dc-49ef-abe3-48ef3c1dbd78', 'property': 'ESTC HOTEL', 'date': '2024-06-05', 'room_type_id': 'RT-0004', 'room_type': 'Double Double Room', 'room_id': 'RM-0009', 'room_number': '109', 'rate_type': 'Rate Include B/F', 'reservation_stay': 'ST2024-5479', 'reservation': 'RS2024-0954', 'guest': '0004', 'input_rate': 400.0, 'discount_amount': 0.0, 'tax_1_rate': 0.0, 'tax_2_rate': 2.0, 'tax_3_rate': 10.0, 'adult': 1, 'child': 0, 'tax_rule': 'Room Charge Tax', 'rate_include_tax': 'Yes', 'is_package': 1, 'package_charge_data': '[{"account_code": "10837", "posting_rule": "Everyday", "charge_rule": "Adult", "rate": 0.0, "adult_rate": 6.0, "child_rate": 0.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}, {"account_code": "10838", "posting_rule": "Everyday", "charge_rule": "Child", "rate": 0.0, "adult_rate": 0.0, "child_rate": 3.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}]', 'is_house_use': 0,
              'is_complimentary': 0}, {'name': '2dc691e9-76dd-4746-bce7-8bcf3b0d55f7', 'property': 'ESTC HOTEL', 'date': '2024-06-06', 'room_type_id': 'RT-0004', 'room_type': 'Double Double Room', 'room_id': 'RM-0009', 'room_number': '109', 'rate_type': 'Rate Include B/F', 'reservation_stay': 'ST2024-5479', 'reservation': 'RS2024-0954', 'guest': '0004', 'input_rate': 400.0, 'discount_amount': 0.0, 'tax_1_rate': 0.0, 'tax_2_rate': 2.0,
                                        'tax_3_rate': 10.0, 'adult': 1, 'child': 0, 'tax_rule': 'Room Charge Tax', 'rate_include_tax': 'Yes', 'is_package': 1, 'package_charge_data': '[{"account_code": "10837", "posting_rule": "Everyday", "charge_rule": "Adult", "rate": 0.0, "adult_rate": 6.0, "child_rate": 0.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}, {"account_code": "10838", "posting_rule": "Everyday", "charge_rule": "Child", "rate": 0.0, "adult_rate": 0.0, "child_rate": 3.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}]', 'is_house_use': 0, 'is_complimentary': 0}, 
                                        {'name': 'dc783cdc-d60c-4d98-8a59-7c7550fd7ffa', 'property': 'ESTC HOTEL', 'date':'2024-06-07', 'room_type_id': 'RT-0004', 'room_type': 'Double Double Room', 'room_id': 'RM-0009', 'room_number': '109', 'rate_type': 'Rate Include B/F', 'reservation_stay': 'ST2024-5479', 'reservation': 'RS2024-0954', 'guest': '0004', 'input_rate': 400.0, 'discount_amount': 0.0, 'tax_1_rate': 0.0, 'tax_2_rate': 2.0, 'tax_3_rate': 10.0, 'adult': 1, 'child': 0, 'tax_rule': 'Room Charge Tax', 'rate_include_tax': 'Yes', 'is_package': 1, 'package_charge_data': '[{"account_code": "10837", "posting_rule": "Everyday", "charge_rule": "Adult", "rate": 0.0, "adult_rate": 6.0, "child_rate": 0.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}, {"account_code": "10838", "posting_rule": "Everyday", "charge_rule": "Child", "rate": 0.0, "adult_rate": 0.0, "child_rate": 3.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}]', 'is_house_use': 0, 'is_complimentary': 0}]
    x = get_new_revenue_forecast_records(data)
    bulk_insert("Revenue Forecast Breakdown",x , chunk_size=10000)
    return x 
    frappe.db.commit()

 
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
    get_charge_breakdown_by_account_code_breakdown.cache_clear()

    if not stay_names:
        stay_names =['ST2024-5397'] #[d["name"] for d in frappe.db.sql("select name from `tabReservation Stay` where reservation='RS2024-0890'",as_dict=1)]
     
    sql="delete from `tabRevenue Forecast Breakdown` where reservation_stay in %(stay_names)s"
 
    frappe.db.sql(sql,{"stay_names":stay_names})
    
    sql="""
        select 
            name,
            stay_room_id,
            property,
            date,
            room_type_id,
            room_type,
            room_id,
            room_number,
            rate_type,
            room_type_alias,
            reservation_stay,
            reservation,
            reservation_type,
            guest,
            guest_type,
            nationality,
            business_source,
            business_source_type,
            input_rate,
            discount_type,
            discount,
            discount_amount,
            tax_1_rate,
            tax_2_rate,
            tax_3_rate,
            adult,
            child,
            tax_rule,
            rate_include_tax,
            is_package,
            package_charge_data,
            is_house_use,
            is_complimentary
        from `tabReservation Room Rate`
     
       where 
            reservation_stay in %(stay_names)s
    """
    
    data = frappe.db.sql(sql,{"stay_names":stay_names},as_dict=1)
 
    # return data
    new_records =  get_new_revenue_forecast_records(data)
    # return new_records
    bulk_insert("Revenue Forecast Breakdown",new_records , chunk_size=10000)
    # update account information
    sql="""
        update `tabRevenue Forecast Breakdown` a 
        JOIN `tabAccount Code` b on b.name = a.account_code
        SET
            a.type=b.type,
            a.parent_account_code = b.parent_account_code,
            a.parent_account_name = b.parent_account_name,
            a.account_group_code = b.account_group,
            a.account_group_name = b.account_group_name,
            a.account_category = b.account_category
        where 
            reservation_stay in %(stay_names)s
    """
    frappe.db.sql(sql,{"stay_names":stay_names})
    if run_commit:
        frappe.db.commit()  
    
    end_time = time.time()

    duration = end_time - start_time
    return("Duration:", duration, "seconds","xx" )

def get_new_revenue_forecast_records(room_rate_data):

    for rate in room_rate_data:
        # we create this to usful with cache
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
        
        account_code_breakdown =[d for d in account_code_breakdown if d["amount"]>0 or d["is_package_account"]==0]
        
        account_code_breakdown = get_charge_breakdown_by_account_code_breakdown(json.dumps(account_code_breakdown)) 
        
        # apply discount discount info to base account
        if account_code_breakdown["base_account"]:
            account_code_breakdown["base_account"]["discount"] = rate["discount"]
            account_code_breakdown["base_account"]["discount_type"] = rate["discount_type"]
            account_code_breakdown["base_account"]["discount_amount"] = rate["discount_amount"]
        # set name and parent reference
        # we dont set name in function get_charge_breakdown_by_account_code_breakdown
        # because of cache problem 
        # and merge this data to 1 array so it easy to loop add batch record to database
        # frappe.throw(str(account_code_breakdown))  
        new_records_data = []
        # 1 base account
        account_code_breakdown["base_account"]["name"] = str(uuid.uuid4())
        account_code_breakdown["base_account"]["parent_reference"] = ""
        new_records_data.append(account_code_breakdown["base_account"])
        for s in [d for d in account_code_breakdown["base_account"]["sub_account"] if d["amount"]>0]:
            s["name"] = str(uuid.uuid4())
            s["parent_reference"] = account_code_breakdown["base_account"]["name"] 
            new_records_data.append(s)
        # 2 package account
        for p in account_code_breakdown["package_accounts"]:
            p["name"] = str(uuid.uuid4())
            p["parent_reference"] = account_code_breakdown["base_account"]["name"] 
            new_records_data.append(p)
            for s in [d for d in p["sub_account"] if d["amount"]>0]:
                s["name"] = str(uuid.uuid4())
                s["parent_reference"] = p["name"] 
                new_records_data.append(s)
       
        # 3 breakdown account
        account_code_breakdown["breakdown_accounts"] = group_breakdown_breakdown_account_code(account_code_breakdown["breakdown_accounts"])
        
        
        for b in account_code_breakdown["breakdown_accounts"]:
            b["name"] = str(uuid.uuid4())
            b["parent_reference"] = account_code_breakdown["base_account"]["name"] 
            new_records_data.append(b)
            for s in [d for d in b["sub_account"] if d["amount"]>0]:
                s["name"] = str(uuid.uuid4())
                # we set parent reference to base account name 
                # because we need this to generate report jurnal posting with out breakdown account code
                
                s["parent_reference"] = account_code_breakdown["base_account"]["name"]
                new_records_data.append(s)
                
        new_records_data = sorted(new_records_data, key=lambda x: x["sort_order"])
         
        
        for acc in  new_records_data:
            doc = frappe.new_doc("Revenue Forecast Breakdown")
            
            doc.name  =acc["name"]
            doc.is_base_transaction = 0 if not "is_base_transaction" in acc else acc["is_base_transaction"]
            doc.parent_reference = acc["parent_reference"]
            doc.stay_room_id = rate["stay_room_id"],
            
            doc.room_rate_id =  rate["name"]
            doc.property = rate["property"]
            doc.guest= rate["guest"]
            doc.guest_type= rate["guest_type"]
            doc.guest_type= rate["guest_type"]

            doc.nationality= rate["nationality"]
            doc.business_source= rate["business_source"]
            doc.business_source_type= rate["business_source_type"]
            doc.room_id= rate["room_id"]
            doc.room_number= rate["room_number"]
            doc.room_type_id= rate["room_type_id"]
            doc.room_type= rate["room_type"]
            doc.room_type_alias= rate["room_type_alias"]
     
            doc.date= rate["date"]
            doc.reservation= rate["reservation"]
            doc.reservation_stay= rate["reservation_stay"]
            doc.reservation_type= rate["reservation_type"]
            doc.rate_type= rate["rate_type"]
            doc.account_code = acc["account_code"]
            doc.input_rate = acc["amount"] if not "input_rate" in acc else acc["input_rate"]
            doc.quantity = 0 if not "quantity" in acc else  acc["quantity"]
            doc.adult = rate["adult"] or 1
            doc.child = rate["child"] or 0
            doc.amount =  acc["amount"]
            doc.price = doc.amount if doc.quantity ==0 else doc.amount / doc.quantity
           
            doc.sort_order = acc["sort_order"]
            doc.is_house_use = rate["is_house_use"]
            doc.is_complimentary = rate["is_complimentary"]
            doc.is_package = 0 if not "is_package" in acc else  acc["is_package"]
            doc.is_package_charge = 0 if not "is_package_charge" in acc else acc["is_package_charge"]
            doc.is_package_breakdown= 0 if not "is_package_breakdown" in acc else acc["is_package_breakdown"]
            doc.discount_type = 'Percent'
            # update discount info
            if "discount" in acc:
                doc.discount = acc["discount"]
            if "discount_type" in acc:
                doc.discount_type = acc["discount_type"]
            if "discount_amount" in acc:
                doc.discount_amount = acc["discount_amount"]
              
            # tax rate 
            doc.rate_include_tax = "" if not "rate_include_tax" in  acc else acc["rate_include_tax"]
            if "tax_1_rate" in acc:
                doc.tax_1_rate = acc["tax_1_rate"]
            if "tax_2_rate" in acc:
                doc.tax_2_rate = acc["tax_2_rate"]
            if "tax_3_rate" in acc:
                doc.tax_3_rate = acc["tax_3_rate"]
                
            doc.total_tax = 0  if not "total_tax" in acc else   acc["total_tax"]
            
            doc.total_amount = doc.amount - (doc.discount_amount or  0)+ (doc.total_tax or 0)
            
            yield doc
            
            
    # return result
    
def group_breakdown_breakdown_account_code(data):
    

    result =[]
    for acc in set([d["account_code"] for d in data]):
        charge = [d for d in data if d["account_code"] ==acc]
        charge = charge[0]
        base_account_data = {
            "account_code":acc,
            "amount":sum([d["amount"] for d in data if d["account_code"] ==acc]),
            "sort_order": charge["sort_order"],
            "is_package_breakdown":1,
            "sub_account":[]

        }
        
        
        # sub account
        sub_accounts = []
        for s in [d for d in data if d["account_code"] == acc]:
            sub_accounts  =  sub_accounts + s["sub_account"]
       
        if sub_accounts:
                for sub_acc in set([d["account_code"] for d in sub_accounts]):
                    sub_charge = [d for d in sub_accounts if d["account_code"] ==sub_acc]
                    sub_charge = sub_charge[0]
                    base_account_data["sub_account"].append ({
                        "account_code":sub_acc,
                        "amount":sum([d["amount"] for d in sub_accounts if d["account_code"] ==sub_acc]),
                        "sort_order": sub_charge["sort_order"],
                        "is_package_breakdown":1

                    })
               
        result.append(base_account_data)    
    return sorted(result, key=lambda x: x["sort_order"])


@lru_cache(maxsize=128)
def get_charge_breakdown_by_account_code_breakdown(account_code_breakdown):
    account_code_breakdown = json.loads(account_code_breakdown)
    # return account_code_breakdown
    tax_data_breakdown = []
    for acc in account_code_breakdown:
        tax_data = get_tax_breakdown( acc["tax_rule"],
                                         rate_include_tax="No" if not acc["rate_include_tax"] else acc["rate_include_tax"], 
                                         tax_1_rate=acc["tax_1_rate"], 
                                         tax_2_rate=acc["tax_2_rate"], 
                                         tax_3_rate=acc["tax_3_rate"],
                                         discount_amount=acc["discount_amount"],
                                         rate=acc["amount"]
                                        )
        
        tax_data["account_code"] = acc["account_code"]
         
        
        tax_data_breakdown.append(tax_data)
        
    breakdown_account_codes = {"package_accounts":[],"breakdown_accounts":[]}
    # 1 Base Account
    base_account = account_code_breakdown[0]
   
   
    base_charge = {
        "account_code":base_account["account_code"],
        "is_base_transaction":1,
        "type":base_account["type"],
        "input_rate":base_account["input_rate"],
        "amount":sum([d["rate"] for d in tax_data_breakdown if 'rate' in d]) or 0,
        "quantity":1,
        "sort_order":1,
        "parent_reference": "",
        "is_package": base_account["is_package"],
        "tax_1_rate": 0 if not "tax_1_rate" in base_account else  base_account["tax_1_rate"],
        "tax_2_rate": 0 if not "tax_2_rate" in base_account else  base_account["tax_2_rate"],
        "tax_3_rate": 0 if not "tax_3_rate" in base_account else  base_account["tax_3_rate"],
        "rate_include_tax":base_account["rate_include_tax"],
        "total_tax":sum(
                d["amount"]
                for entry in tax_data_breakdown if "tax_data_list" in  entry
                for d in entry["tax_data_list"]
            ),
        "discount_amount":sum([d["discount_amount"] for d in account_code_breakdown   if "discount_amount" in d]),
        "sub_account":[]
    }
    breakdown_account_codes["base_account"]= base_charge

    # discount
    if base_account["discount"]>0:
        discount_amount = sum([d["discount_amount"] for d in account_code_breakdown   if "discount_amount" in d])
        base_charge["sub_account"].append({
            "account_code":base_account["discount_account"],
            "amount":discount_amount,
            "note":"Base Discount"  ,
            "sort_order":2  ,
            
            # "is_package": base_account["is_package"]     
        })
         
 
    
    if "tax_1_account" in base_account and base_account["tax_1_account"]:
        base_charge["sub_account"].append({
            "account_code":base_account["tax_1_account"],
            "amount":sum(
                d["amount"]
                for entry in tax_data_breakdown if "tax_data_list" in entry
                for d in entry["tax_data_list"]
                if d["tax_name"] == base_account["tax_1_name"]
            ),
            "sort_order":3  ,
            # "is_package": base_account["is_package"]
            })

    if "tax_2_account" in base_account and base_account["tax_2_account"]:
        base_charge["sub_account"].append({
            "account_code":base_account["tax_2_account"],
            "amount":sum(
                d["amount"]
                for entry in tax_data_breakdown if "tax_data_list" in entry
                for d in entry["tax_data_list"]
                if d["tax_name"] == base_account["tax_2_name"]
            ),
            "sort_order":4  ,
            # "is_package": base_account["is_package"]  
        })
    if "tax_3_account" in base_account and base_account["tax_3_account"]:
        base_charge["sub_account"].append({
            "account_code":base_account["tax_3_account"],
            "amount":sum(
                d["amount"]
                for entry in tax_data_breakdown if "tax_data_list" in entry
                for d in entry["tax_data_list"]
                if d["tax_name"] == base_account["tax_3_name"]
            ),
            "sort_order":5  ,
            # "is_package": base_account["is_package"] 
            
        })
    # package account breakdown
    package_sort_order = 100
    
    for p in [d for d in account_code_breakdown if "is_package_account" in d and  d["is_package_account"]==1]:
        package_account = [d for d in tax_data_breakdown if d["account_code"]== p["account_code"]]
        
        if package_account:
            package_account = package_account[0]
           
            # frappe.throw(str(package_account))
            package_charge ={
                "account_code":p["account_code"],
                "is_base_transaction":1,
                "type":p["type"],
                "input_rate":p["input_rate"],
                "amount":package_account["rate"],
                "quantity":0 if not "quantity" in  p else   p["quantity"],
                "sort_order": package_sort_order + 1,
                "is_package_charge":1,
                "tax_1_rate": 0 if not "tax_1_rate" in p else  p["tax_1_rate"],
                "tax_2_rate": 0 if not "tax_2_rate" in p else  p["tax_2_rate"],
                "tax_3_rate": 0 if not "tax_3_rate" in p else  p["tax_3_rate"],
                "discount_amount":p["discount_amount"],
                "total_tax": 0 if not "tax_data_list" in package_account else sum([d["amount"] for  d in package_account["tax_data_list"]]),
                "sub_account":[],
                "rate_include_tax":p["rate_include_tax"]
            }
            # package_charge["rate"] = 
            breakdown_account_codes["package_accounts"].append(package_charge)
            # breakdown account
            if p["breakdown_account_code"]:
                breakdown_charge = {
                    "account_code":p["breakdown_account_code"],
                    "amount":package_account["rate"],
                    "note":"Breakdown Account of {}".format(p["account_code"]),
                    "sort_order":10  ,
                    "is_package_breakdown":1,
                    "sub_account":[]
                }
                breakdown_account_codes["breakdown_accounts"].append(breakdown_charge)
                
            # discount
            if "discount" in p and   p["discount"]>0:
                package_charge["sub_account"].append({
                    "account_code":p["discount_account"],
                    "amount":p["discount_amount"],
                    "note":"Package Discount",
                     "sort_order": package_sort_order + 2,
                     "is_package_charge":1
                })
                # breakdown discount account
                if p["discount_breakdown_account_code"]:
                    breakdown_charge["sub_account"].append({
                        "account_code":p["discount_breakdown_account_code"],
                        "amount":p["discount_amount"],
                        "note":"Discount Breakdown Account",
                        "sort_order":11 ,
                        "is_package_breakdown":1
                        
                })
            
            # tax_1_account amount
            if p["tax_1_rate"] > 0:
                package_charge["sub_account"].append({
                    "account_code":p["tax_1_account"],
                    "amount":package_account["tax_1_amount"],
                     "sort_order": package_sort_order + 3,

                     "is_package_charge":1
                })
                # tax 1 breakdown account
                if p["tax_1_breakdown_account_code"]  :
                    
                    breakdown_charge["sub_account"].append({
                        "account_code":p["tax_1_breakdown_account_code"],
                        "amount":package_account["tax_1_amount"],
                        "note":"Tax 1 Breakdown Account",
                        "sort_order":12 ,
                        "is_package_breakdown":1
                        
                })
            # tax_2_account amount
            if p["tax_2_rate"] > 0:
                package_account["sub_account"].append({
                    "account_code":p["tax_2_account"],
                    "amount":package_account["tax_2_amount"],
                     "sort_order": package_sort_order + 4,
                     "is_package_charge":1
                })
                # tax 2 breakdown account
                if p["tax_2_breakdown_account_code"]:
                    breakdown_charge["sub_account"].append({
                        "account_code":p["tax_2_breakdown_account_code"],
                        "amount":package_account["tax_2_amount"],
                        "note":"Tax 2 Breakdown Account",
                        "sort_order":13  ,
                        "is_package_breakdown":1
                        
                    })
            # tax_3_account amount
            if p["tax_3_rate"] > 0:
                package_charge["sub_account"].append({
                    "account_code":p["tax_3_account"],
                    "amount":package_account["tax_3_amount"],
                     "sort_order": package_sort_order + 5,
                     "is_package_charge":1
                })
                
                # tax 3 breakdown account
                if p["tax_3_breakdown_account_code"]:
                    breakdown_charge["sub_account"].append({
                        "account_code":p["tax_3_breakdown_account_code"],
                        "amount":package_account["tax_3_amount"],
                        "note":"Tax 3 Breakdown Account",
                        "sort_order":14  ,
                        "is_package_breakdown":1
                    })
        package_sort_order = package_sort_order + 100
        
    breakdown_account_codes["base_account"]["sub_account"] = [d for d in breakdown_account_codes["base_account"]["sub_account"]  if d["amount"]>0]
    
    return  breakdown_account_codes
        
@lru_cache(maxsize=128)
def get_room_rate_account_code_breakdown(room_rate_data):
    room_rate_data = {key: value for key, value in room_rate_data}
    base_account_codes=[]
    
    rate_type_doc = get_rate_type_doc(room_rate_data['rate_type'])
    
    account_code_doc = get_account_code_doc(rate_type_doc.account_code)
    base_code = {
                "account_code":rate_type_doc.account_code,
                "account_name":account_code_doc.account_name,
                "is_package_account":0,
                 "allow_discount":account_code_doc.allow_discount,
                "parent_account_name":account_code_doc.parent_account_name,
                "input_rate": room_rate_data["input_rate"],
                "amount":0,
                "tax_1_rate":0,
                "tax_2_rate":0,
                "tax_3_rate":0,
                "discount":0,
                "discount_amount":0,
                "type":account_code_doc.type,
                "tax_rule":"",
                "quantity":0,
                "is_package":room_rate_data["is_package"]
            }
    # sub account of main account
    base_code["tax_rule"] = room_rate_data["tax_rule"]
    base_code["rate_include_tax"] = room_rate_data["rate_include_tax"]
 
    if room_rate_data["tax_rule"]:
        tax_rule_doc = get_tax_rule_doc(room_rate_data["tax_rule"])
        base_code["tax_1_name"] = tax_rule_doc.tax_1_name
        base_code["tax_2_name"] = tax_rule_doc.tax_2_name
        base_code["tax_3_name"] = tax_rule_doc.tax_3_name
        if tax_rule_doc.tax_1_account:
            base_code["tax_1_account"] = tax_rule_doc.tax_1_account
            base_code["tax_1_rate"] = room_rate_data["tax_1_rate"] or 0
        
        if tax_rule_doc.tax_2_account:
            base_code["tax_2_account"] = tax_rule_doc.tax_2_account
            base_code["tax_2_rate"] = room_rate_data["tax_2_rate"] or 0
        
        if tax_rule_doc.tax_3_account:
            base_code["tax_3_account"] = tax_rule_doc.tax_3_account
            base_code["tax_3_rate"] = room_rate_data["tax_3_rate"] or 0
        
    if account_code_doc.allow_discount and account_code_doc.discount_account:
        base_code["discount_account"]=account_code_doc.discount_account     
    base_account_codes.append(base_code)    
    if room_rate_data["is_package"] ==1 and (room_rate_data["input_rate"] or 0)>0:
 
        package_account_codes =   package_base_account_code_charge_breakdown( tuple(sorted(room_rate_data.items())))
        base_code["amount"] = room_rate_data["input_rate"] - sum([d["amount"] for d in package_account_codes if d["is_package_account"]==1])
        base_account_codes =  base_account_codes + package_account_codes
    else:
         base_code["amount"] = room_rate_data["input_rate"]

    base_code["amount"] = 0 if base_code["amount"]<=0 else base_code["amount"]

    # set discount 
    discountable_amount = room_rate_data["input_rate"] - sum([d["amount"] for d in base_account_codes if d["allow_discount"]==0])
    for a in [d for d in base_account_codes if d["allow_discount"]==1]:
        room_rate_data["discount_amount"] = room_rate_data["discount_amount"] or 0
        a["discount"] =  room_rate_data["discount_amount"] /  ( 1 if discountable_amount==0 else  discountable_amount )
        if a["discount"]>1:
            a["discount"] =1
            
        a["discount_amount"] = a["amount"] * a["discount"]
    
    return base_account_codes

@lru_cache(maxsize=128)
def package_base_account_code_charge_breakdown(room_rate_data):
    
    room_rate_data = {key: value for key, value in room_rate_data}
    
    data = []
    for p in json.loads( room_rate_data["package_charge_data"]) or []:
        account_code_doc = get_account_code_doc(p["account_code"])
        
        doc = {
            "account_code": p["account_code"],
            "allow_discount": account_code_doc.allow_discount,
            "parent_account_name": account_code_doc.parent_account_name,
            "is_package_account": 1,
            "is_package_charge":1,
            "tax_1_rate":0,
            "tax_2_rate":0,
            "tax_3_rate":0,
            "discount":0,
            "discount_amount":0,
            "tax_rule":"",
            "rate_include_tax": "No",
           "type":account_code_doc.type,
           "account_name":account_code_doc.account_name,
           "breakdown_account_code": p["breakdown_account_code"],
           "discount_breakdown_account_code": p["discount_breakdown_account_code"],
           "tax_1_breakdown_account_code": p["tax_1_breakdown_account_code"],
           "tax_2_breakdown_account_code": p["tax_2_breakdown_account_code"],
           "tax_3_breakdown_account_code": p["tax_3_breakdown_account_code"],
        }
        if p["charge_rule"] =="Stay":
            doc["quantity"] = 1
            
            doc["amount"] = p["rate"]
            doc["input_rate"] = p["rate"]
        elif p["charge_rule"] =="Adult":
            doc["quantity"] = room_rate_data["adult"]
            doc["amount"] = doc["quantity"] * p["adult_rate"] 
            doc["input_rate"] = p["adult_rate"]
        else:
            # child charge rull
            doc["quantity"] = room_rate_data["child"]
            doc["amount"] = doc["quantity"] * p["child_rate"] 
            doc["input_rate"] = p["child_rate"]
        
        
        
        
        if account_code_doc.tax_rule:
            tax_rule_doc = get_tax_rule_doc(account_code_doc.tax_rule)
            doc["tax_rule"] = account_code_doc.tax_rule
            doc["rate_include_tax"] ="Yes" if  tax_rule_doc.is_rate_include_tax else 'No'
            if tax_rule_doc.tax_1_account and   tax_rule_doc.tax_1_rate:
                doc["tax_1_account"] = tax_rule_doc.tax_1_account
                doc["tax_1_rate"] = tax_rule_doc.tax_1_rate
            if tax_rule_doc.tax_2_account and  tax_rule_doc.tax_2_rate :
                doc["tax_2_account"] = tax_rule_doc.tax_2_account
                doc["tax_2_rate"] =  tax_rule_doc.tax_2_rate
            if tax_rule_doc.tax_3_account and tax_rule_doc.tax_3_rate:
                doc["tax_3_account"] = tax_rule_doc.tax_3_account
                doc["tax_3_rate"] = tax_rule_doc.tax_3_rate

        if account_code_doc.allow_discount and account_code_doc.discount_account:
           doc["discount_account"]= account_code_doc.discount_account 
       
        data.append(doc) 
    return data  


# def get_new_revenue_forecast_doc(room_rate_data, account_code, rate):
#     doc = frappe.new_doc("Revenue Forecast Breakdown")
#     doc.name  = str(uuid.uuid4())
#     doc.room_rate_id = room_rate_data["name"]
#     doc.reservation_stay = room_rate_data["reservation_stay"]
#     doc.reservation= room_rate_data["reservation"]
#     doc.property = room_rate_data["property"]
#     doc.guest = room_rate_data["guest"]
#     doc.date = room_rate_data["date"]
#     doc.room_type_id = room_rate_data["room_type_id"]
#     doc.room_type = room_rate_data["room_type"]
#     doc.room_id = room_rate_data["room_id"]
#     doc.room_number = room_rate_data["room_number"]
#     doc.account_code = account_code
#     doc.amount = rate
#     return doc
 
@frappe.whitelist()
def get_room_rate_calculation(room_rate_data=None,rate=100):
    data = []
    if not room_rate_data:
        room_rate_data ={
            "rate_type": "Rate Include B/F",
            "tax_rule": "Room Charge Tax",
            "rate_include_tax": "Yes",
            "tax_1_rate": 0,
            "tax_2_rate": 2,
            "tax_3_rate": 10,
            "input_rate": 20,
            "discount_type": "Percent",
            "discount": 10,
            "adult": 4,
            "child": 1,
            "is_package": 1,
            "package_charge_data": "[{\"account_code\": \"10837\", \"posting_rule\": \"Everyday\", \"charge_rule\": \"Adult\", \"rate\": 0.0, \"adult_rate\": 6.0, \"child_rate\": 0.0, \"breakdown_account_code\": \"10119\", \"discount_breakdown_account_code\": \"40103\", \"tax_1_breakdown_account_code\": \"\", \"tax_2_breakdown_account_code\": \"\", \"tax_3_breakdown_account_code\": \"20107\"}, {\"account_code\": \"10838\", \"posting_rule\": \"Everyday\", \"charge_rule\": \"Child\", \"rate\": 0.0, \"adult_rate\": 0.0, \"child_rate\": 3.0, \"breakdown_account_code\": \"10119\", \"discount_breakdown_account_code\": \"40103\", \"tax_1_breakdown_account_code\": \"\", \"tax_2_breakdown_account_code\": \"\", \"tax_3_breakdown_account_code\": \"20107\"}]"
            }
    if "discount_amount" not in room_rate_data:
        room_rate_data["discount_amount"] = 0
    room_rate_data["discount"] = room_rate_data["discount"] or 0
        
    account_codes = get_room_rate_account_code_breakdown(tuple(sorted(room_rate_data.items())))
    if room_rate_data["discount"]>0:
        if room_rate_data["discount_type"]=="Amount":
            discountable_amount = sum(d["amount"] for d in account_codes if d["allow_discount"]==1)
            
            room_rate_data["discount"] = room_rate_data["discount"] / (1 if discountable_amount==0 else discountable_amount)

        
        else:
            # convert discount to decimal number 10%=0.1
            room_rate_data["discount"] = room_rate_data["discount"] / 100
        
        for d in [x for x in account_codes if x["allow_discount"] == 1]:
            d["discount_amount"] = d["amount"] * room_rate_data["discount"] 
    # return account_codes
    for acc in account_codes:
        tax_data  =  get_tax_breakdown(
                tax_rule=acc["tax_rule"],
                rate_include_tax=acc["rate_include_tax"], 
                tax_1_rate=acc["tax_1_rate"],
                tax_2_rate=acc["tax_2_rate"], 
                tax_3_rate=acc["tax_3_rate"],
                discount_amount=acc["discount_amount"],
                rate=acc["amount"]
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
    
    return {
        "room_charge_data": data[0],
        "package_charge_data": [d for d in data if d["is_package"] == 1],
        "discount_amount": sum(d["discount_amount"] for d in data),
        "total_tax": sum(d["total_tax"] for d in data),
        "total_amount": sum(d["total_amount"] for d in data)
    }


# this function is use to test performance
@frappe.whitelist()
def test_rate_breakdown():
    start_time = time.time()
    # get_room_rate_breakdown.cache_clear()
    data = frappe.db.sql("""select  
                         rate_type,
                         tax_rule,
                         rate_include_tax,
                         tax_1_rate,
                         tax_2_rate,
                         tax_3_rate,
                         input_rate,
                         is_package,
                         discount_type,
                         discount,
                         discount_amount,
                         adult,
                         child,
                         coalesce(package_charge_data,'[]') as package_charge_data
                         from `tabReservation Room Rate` limit 50000""",as_dict=1)
    
    result = []
    for x in data:
        result.append(get_room_rate_breakdown(json.dumps(x)))
        
    end_time = time.time()
    duration = end_time - start_time
    return("Duration:", duration, "seconds",result)
 
# this function return room rate,total_tax, total_other charge and total all rate
@lru_cache(maxsize=1024)
def get_room_rate_breakdown(room_rate_data=None,rate=100):
    data = []
    room_rate_data = json.loads(room_rate_data)

    if not room_rate_data:
        room_rate_data = {
            "rate_type":"Rate Include B/F",
            "tax_rule":"Room Charge Tax",
            "rate_include_tax":"No",
            "tax_1_rate":5,
            "tax_2_rate":2,
            "tax_3_rate":10,
            "input_rate":float(rate),
            "is_package":1,
            "discount_type":"Percent",
            "discount":20,
            "discount_amount":0,
            "adult":2,
            "child":1,
            "package_charge_data":json.dumps([{"account_code": "10837", "posting_rule": "Everyday", "charge_rule": "Adult", "rate": 0.0, "adult_rate": 6.0, "child_rate": 0.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}, {"account_code": "10838", "posting_rule": "Everyday", "charge_rule": "Child", "rate": 0.0, "adult_rate": 0.0, "child_rate": 3.0, "breakdown_account_code": "10119", "discount_breakdown_account_code": "40103", "tax_1_breakdown_account_code": "", "tax_2_breakdown_account_code": "", "tax_3_breakdown_account_code": "20107"}])
        }

    if "discount_amount" not in room_rate_data:
        room_rate_data["discount_amount"] = 0
        
    account_codes = get_room_rate_account_code_breakdown(tuple(sorted(room_rate_data.items())))
    room_rate_data["discount"] = room_rate_data["discount"] or 0
    if room_rate_data["discount"]>0:
        if room_rate_data["discount_type"]=="Amount":
            discountable_amount = sum(d["amount"] for d in account_codes if d["allow_discount"]==1)
            room_rate_data["discount"] = room_rate_data["discount"] / (1 if discountable_amount==0 else discountable_amount)
        else:
            # convert discount to decimal number 10%=0.1
            room_rate_data["discount"] = room_rate_data["discount"] / 100
        
        for d in [x for x in account_codes if x["allow_discount"] == 1]:
            
            d["discount_amount"] = d["amount"] * room_rate_data["discount"] 
    # return account_codes
    
    for acc in account_codes:
        tax_data  =  get_tax_breakdown(
                tax_rule=acc["tax_rule"],
                rate_include_tax=acc["rate_include_tax"], 
                tax_1_rate=acc["tax_1_rate"],
                tax_2_rate=acc["tax_2_rate"], 
                tax_3_rate=acc["tax_3_rate"],
                discount_amount=acc["discount_amount"],
                rate=acc["amount"]
        )
        
        tax_data["account_name"] = acc["account_name"]
        tax_data["allow_discount"] = acc["allow_discount"]
        tax_data["discount_amount"] = acc["discount_amount"]
        tax_data["parent_account_name"] = "" if not  "parent_account_name" in acc else  acc["parent_account_name"]
        
        tax_data["is_package"] = 0 if not "is_package_account" in acc      else  acc["is_package_account"]
        
        data.append(
            tax_data
        )
    tax_rule_data = ""
    if data:
        tax_rule_data = '{}' if not "tax_rule_data" in   data[0] else  data[0]["tax_rule_data"]
 
    return {
        "tax_rule_data":tax_rule_data,
        "total_room_charge":sum(d["total_amount"] for d in data if d["parent_account_name"]=='Room Charge'),
        "total_other_charge":sum(d["total_amount"] for d in data if d["parent_account_name"]!='Room Charge'),
        "discount_amount": sum(d["discount_amount"] for d in data),
        "total_tax": sum(d["total_tax"] for d in data),
        "total_amount": sum(d["total_amount"] for d in data)
    }

