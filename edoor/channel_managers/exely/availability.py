import frappe
import requests
import xmltodict
from datetime import datetime
from edoor.channel_managers.exely.utils import get_exely_property_code,get_exely_room_type_code
from edoor.channel_managers.exely.soap_request import send_soap_request
from frappe.utils import getdate, add_days,now,today
from itertools import groupby
import json
from lxml import etree

from frappe.utils import add_to_date, now_datetime



@frappe.whitelist()
def testme():
    return update_room_availability("ESTC HOTEL 6")
  

@frappe.whitelist(methods="POST")
def  update_room_availability(property):
    
    sql="""
        SELECT t.value, t.room_type, t.date, t.creation
        FROM `tabChannel Manager Sync Data Log` t
        JOIN (
            SELECT MAX(creation) AS max_creation, room_type, date
            FROM `tabChannel Manager Sync Data Log`
            where
                provider = "Exely" and 
                property = %(property)s and 
                request_type = 'OTA_HotelAvailNotifRQ'
                
            GROUP BY room_type, date
        ) m
        ON t.creation = m.max_creation
            AND t.room_type = m.room_type
            AND t.date = m.date 
        where
            t.provider = "Exely" and 
            t.property = %(property)s and 
            t.request_type = 'OTA_HotelAvailNotifRQ'
        order by
            t.date
        ;
    """
    data = frappe.db.sql(sql,{"property":property},as_dict = 1)
    
    # frappe.throw(str(data))
    # frappe.throw(str(max( [frappe.utils.get_datetime( d.get("creation")) for d in data])))

    if data:
        # try:
        
        room_available_data = group_availability(data)
        
        if room_available_data:
            soap_body = build_availability_xml(property=property, data = room_available_data)
           

            response =  send_soap_request(property,"OTA_HotelAvailNotifRQ",soap_body)
            
        
            # return response

            # save log
            doc = frappe.get_doc({
                    "property": property,
                    "doctype":"Channel Manager Sync Log",
                    "provider":"Exely",
                    "request_type":"OTA_HotelAvailNotifRQ",
                    "title":"Room Availability",
                    "is_synced" : response.get("status") or False,
                    "data": frappe.as_json(data),
                    "response":frappe.as_json(room_available_data)
            }).insert(ignore_permissions=True)
            
            
            
            
            if not doc.is_synced:
                doc.add_comment(
                    comment_type="Comment",
                    text= frappe.as_json(response.get("data"))
                )

            
            # delete sync record
            sql = """
                delete from `tabChannel Manager Sync Data Log` 
                where 
                    (
                        property=%(property)s and 
                        provider = 'Exely' and 
                        request_type = 'OTA_HotelAvailNotifRQ' and
                        creation<=%(datetime)s ) 
                    OR (  
                        date < CURDATE() and
                        property=%(property)s and 
                        provider = 'Exely' and 
                        request_type = 'OTA_HotelAvailNotifRQ'
                    )
                    """
            frappe.db.sql(sql,{"property": property, "datetime":max( [frappe.utils.get_datetime( d.get("creation")) for d in data])})


        # except Exception:

        #     doc = frappe.get_doc({
        #             "property": property,
        #             "doctype":"Channel Manager Sync Log",
        #             "provider":"Exely",
        #             "request_type":"OTA_HotelAvailNotifRQ",
        #             "is_synced" : False,
        #             "data": frappe.as_json(data)
        #     }).insert(ignore_permissions=True)

        #     if not doc.is_synced:
                    
        #         doc.add_comment(
        #             comment_type="Comment",
        #             text= frappe.get_traceback()
        #         )

        

        frappe.db.commit()


def group_availability(data):
 
    # remove past date
    data = [d for d in data if getdate( d.get("date"))>=getdate(today())]
    
 
    

    # sort by room_type and date
    
    data = sorted(data, key=lambda x: (x["room_type"], x["date"]))
    
    results = []

    for room_type, items in groupby(data, key=lambda x: x["room_type"]):

        items = list(items)

        start = items[0]["date"]
        end = items[0]["date"]
        last_date = getdate(start)
        booking_limit = items[0]["value"]

        for r in items[1:]:

            current_date = getdate(r["date"])

            if (
                r["value"] == booking_limit
                and current_date == add_days(last_date, 1)
            ):
                end = r["date"]

            else:

                results.append({
                    "room_type": room_type,
                    "start": start,
                    "end": end,
                    "booking_limit": booking_limit
                })

                start = r["date"]
                end = r["date"]
                booking_limit = r["value"]

            last_date = current_date

        results.append({
            "room_type": room_type,
            "start": start,
            "end": end,
            "booking_limit": booking_limit
        })
 
    return results

def build_availability_xml(property,data):

    hotel_code = get_exely_property_code(property)
    

    root = etree.Element(
        "OTA_HotelAvailNotifRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )


    messages = etree.SubElement(root, "AvailStatusMessages", HotelCode=hotel_code)
    
    for r in data:
        msg = etree.SubElement(
            messages,
            "AvailStatusMessage",
            BookingLimit=str(r["booking_limit"])
        )
 

        etree.SubElement(
            msg,
            "StatusApplicationControl",
            Start=str(r["start"]),
            End=str(r["end"]),
            InvTypeCode=get_exely_room_type_code(r.get("room_type"))
        )

    return etree.tostring(root, pretty_print=True).decode()
