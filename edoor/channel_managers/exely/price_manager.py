import frappe
from edoor.channel_managers.utils import group_date_ranges,get_channal_manager_info,get_occupancy_codes
from edoor.channel_managers.exely.utils import get_exely_property_code,get_exely_room_type_code
from edoor.channel_managers.exely.soap_request import send_soap_request
from lxml import etree

from decimal import Decimal

# flow to sync rate 
# get use occupancy code from cm data log, G1,G2,...
# convert occupancy code from cm data log from row to column then select unique rate value 
# take unique rate value for occupancy code find date that use it 
# after get dates then convert date list to period match with uniquevalue
# build uiqnue value with period to XML to send to chanel manager
# channel manager sync by property code and sync by rate type (rate plan)

# synch limitaion, this limitation include rate, restriction, discount, serverice
# 1 second limit max 1460 value change 
# 3 minute limit max 4380 value change
# 1 hour limit max 13140 value change
# 1 day limit max 43800 value change



@frappe.whitelist()
def sync_room_rate(property=None):
    if not property:
        properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    else:
        properties = [{"name":property}]

    for p in properties:
        rate_types = frappe.db.sql("select distinct room_type,rate_type from `tabChannel Manager Sync Data Log` where property = %(property)s and provider='Exely' and request_type='OTA_HotelRateAmountNotifRQ'",{"property":p.get("name")},as_dict = 1)
        
        if len(rate_types)>0:
            
            for rp in set([d.get("rate_type") for d in rate_types]):
                room_types = [d.get("room_type") for d in rate_types if d.get("rate_type") == rp]
               
                group_data = get_group_room_rate_data(room_types,rp)
                soap_body = build_room_rate_xml(property = p.get("name"), group_data=group_data,rate_type = rp)
                response =  send_soap_request(p.get("name"),"OTA_HotelRateAmountNotifRQ",soap_body)
                
                
                delete_synced_data_log(room_types)

    frappe.db.commit()
    # chekc if success and fail

    # send socket message to client

    return "done"


def delete_synced_data_log(room_types,run_commit = True):
    sql="""
        delete from `tabChannel Manager Sync Data Log`
        where
            room_type in %(room_types)s and 
            request_type = 'OTA_HotelRateAmountNotifRQ' and 
            provider = 'Exely'
    """
    frappe.db.sql(sql, {"room_types":room_types})
    if run_commit:
        frappe.db.commit()


def get_group_room_rate_data(room_types,rate_type):
    occupancy_codes = get_use_occupancy_codes({
        "room_types":room_types,
        "rate_type":rate_type
    })
    
    unique_data =  get_unique_room_rate_values_by_occupancy_codes(room_types=room_types,occupancy_codes=occupancy_codes,rate_type=rate_type)

    for d in unique_data:
        d["period"] =  get_period(d,rate_type)
    return unique_data


def get_period(data,rate_type):
    occupancy_fields =  [k for k in data.keys() if k != "room_type"]
    occupancy_sql =",".join( [
            "max(CASE WHEN a.occupancy_code = '{0}' THEN coalesce(value,0) ELSE 0 END)  AS {0}".format(d)
        for d in  occupancy_fields])


    
    sql = """
        select  
            date
        FROM (
            select 
                date, 
                {occupancy_sql}
            from 
                `tabChannel Manager Sync Data Log` a 
            where
                a.room_type = %(room_type)s and 
                a.provider = 'Exely' AND 
                a.request_type = 'OTA_HotelRateAmountNotifRQ' and 
                rate_type = %(rate_type)s
            group by 
                date
        ) as data
        WHERE
            {occupancy_filter} 
        order by 
            date

    """.format(
        occupancy_sql = occupancy_sql,
        occupancy_fields = ",".join(occupancy_fields),
        occupancy_filter = " and ".join( [ "{0}=%({0})s".format(x) for x in  occupancy_fields])
        )
     
    
    data = frappe.db.sql(sql, {**data, "rate_type": rate_type},as_dict=1)

    return group_date_ranges(data)
  


def get_unique_room_rate_values_by_occupancy_codes(room_types,occupancy_codes,rate_type):
    # prepare dynamic sql 

    occupancy_sql =",".join( [
             "max(CASE WHEN a.occupancy_code = '{0}' THEN coalesce(value,0) ELSE 0 END)  AS {0}".format(d.get("occupancy_code"))
         for d in  occupancy_codes])

    sql = """
        select 
            distinct 
            room_type,
            {occupancy_field}
        FROM (
            select 
                room_type, 
                {occupancy_sql}
            from 
                `tabChannel Manager Sync Data Log` a 
            where
                a.room_type in %(room_types)s and 
                a.provider = 'Exely' AND 
                a.request_type = 'OTA_HotelRateAmountNotifRQ' and 
                a.rate_type = %(rate_type)s
            group by 
                date, 
                room_type
        ) as data
    """.format(
        occupancy_sql = occupancy_sql,
        occupancy_field = ",".join([d.get("occupancy_code") for d in occupancy_codes])
    )
    
    return frappe.db.sql(sql,{"room_types":room_types,"rate_type":rate_type},as_dict=1)



def get_use_occupancy_codes(filters):
    sql = """
        select 
            distinct 
            a.occupancy_code,
            b.min_age,
            b.max_age
        from `tabChannel Manager Sync Data Log` a 
        join `tabOccupancy Code`  b on b.name = a.occupancy_code
        where
            a.provider= 'Exely' and
            a.request_type = 'OTA_HotelRateAmountNotifRQ'  and 
            a.room_type in %(room_types)s and 
            a.rate_type = %(rate_type)s
    """
    return frappe.db.sql(sql, filters,as_dict = 1)


def build_room_rate_xml(property,group_data,rate_type):
     
    cm_info = get_channal_manager_info(property)
    rate_plan_code = [d for d in cm_info.get("rate_plans") if d.get("edoor_rate_plan") == rate_type]
    if len(rate_plan_code) == 0:
        frappe.throw("Sync room rate to exely channel manager fail. No rate plan code mapping for rate type " + rate_type)
    rate_plan_code = rate_plan_code[0].get("rate_plan_code")

    root = etree.Element(
        "OTA_HotelRateAmountNotifRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )


    RateAmountMessages = etree.SubElement(root, "RateAmountMessages", HotelCode=cm_info.get("property_code"))
    
    for rt in set([d.get("room_type") for d in group_data]):
        cm_room_type = get_exely_room_type_code(rt)
        
        RateAmountMessage = etree.SubElement(RateAmountMessages, "RateAmountMessage")
        # status control set room type code and rate plan code
        StatusApplicationControl = etree.SubElement(
                                    RateAmountMessage, 
                                    "StatusApplicationControl",
                                    InvTypeCode=cm_room_type,
                                    RatePlanCode=rate_plan_code)
        # Rates
        Rates = etree.SubElement(
            RateAmountMessage, 
            "Rates",
        )

        rate_data = [d for d in group_data if d.get("room_type") == rt]
        # Rate by period
        for rate in rate_data:
            
            for pr in rate.get("period"):
                Rate = etree.SubElement(
                    Rates, 
                    "Rate",
                    Start = str(pr.get("start_date")),
                    End = str(pr.get("end_date")) 
                )
                # add rate to Rate
                get_BaseByGuestAmts_xml(Rate,rate)

 
    return etree.tostring(root, pretty_print=True).decode()

def get_BaseByGuestAmts_xml( node, rate_data):
    occupancy_codes = get_occupancy_codes()
    # Main Guest
    main_adult = [d for d in occupancy_codes if d.get("occupancy_type") =="Main Guest Adult"]
    main_adult = {item["name"]: item for item in main_adult}
    main_child = [d for d in occupancy_codes if d.get("occupancy_type") =="Main Guest Child"]
    main_child = {item["name"]: item for item in main_child}
    # Extra Bed 
    # adult 
    extra_bed_adult = [d for d in occupancy_codes if d.get("occupancy_type") =="Extra Bed Adult"]
    extra_bed_adult = {item["name"]: item for item in extra_bed_adult}
    # exttra bed child 
    extra_bed_child = [d for d in occupancy_codes if d.get("occupancy_type") =="Extra Bed Child"]
    extra_bed_child = {item["name"]: item for item in extra_bed_child}

    # exttra bed child 
    child_without_bed = [d for d in occupancy_codes if d.get("occupancy_type") =="Child Without Bed"]
    child_without_bed = {item["name"]: item for item in child_without_bed}
    
    BaseByGuestAmts =   etree.SubElement(
                    node, 
                    "BaseByGuestAmts",       
                )

    # set node extra bed 
    AdditionalGuestAmounts = None
 

    

    
    if  any( 
            x in list(rate_data.keys()) 
            for x in 
            [d.get("name") for d in occupancy_codes if d.get("occupancy_type") in ["Extra Bed Adult","Extra Bed Child","Child Without Bed"]]
        ):
         
            AdditionalGuestAmounts =   etree.SubElement(
                    node, 
                    "AdditionalGuestAmounts",       
                )


    for key, value in rate_data.items():
        if key in main_adult:
            BaseByGuestAmt =   etree.SubElement(
                    BaseByGuestAmts, 
                    "BaseByGuestAmt",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    NumberOfGuests= str( main_adult.get(key).get("occupancy")  )
                )
        if key in main_child:
            BaseByGuestAmt =   etree.SubElement(
                    BaseByGuestAmts, 
                    "BaseByGuestAmt",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    MinAge= str( main_child.get(key).get("min_age")  ),
                    MaxAge= str( main_child.get(key).get("max_age")  )
                )
        # Extra guest adult
        if key in extra_bed_adult:
            AdditionalGuestAmount =  etree.SubElement(
                    AdditionalGuestAmounts, 
                    "AdditionalGuestAmount",    
                    AmountAfterTax=str(normalize_amount(value) or 0)
            )
        
        # Extra bed child
        if key in extra_bed_child:
            AdditionalGuestAmount =  etree.SubElement(
                    AdditionalGuestAmounts, 
                    "AdditionalGuestAmount",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    MinAge= str( extra_bed_child.get(key).get("min_age")  ),
                    MaxAge= str( extra_bed_child.get(key).get("max_age")  )
            )

        # additional child without bed
        # BedRequired
        if key in child_without_bed:
            AdditionalGuestAmount =  etree.SubElement(
                    AdditionalGuestAmounts, 
                    "AdditionalGuestAmount",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    MinAge= str( extra_bed_child.get(key).get("min_age")  ),
                    MaxAge= str( extra_bed_child.get(key).get("max_age")  ),
                    BedRequired = "False"
            )

        


def normalize_amount(value):
    d = Decimal(value)
  
    if d == d.to_integral():
        return int(d)

    # otherwise return float without trailing zeros
    return float(d.normalize())
    