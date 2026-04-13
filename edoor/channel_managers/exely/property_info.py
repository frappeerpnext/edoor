import frappe
import requests
import xmltodict
from datetime import datetime
import json
from .soap_request import get_exely_config, send_soap_request


def ensure_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_room_types_from_response(data):
    room_types = (
        data.get("data", {})
            .get("s:Envelope", {})
            .get("s:Body", {})
            .get("OTA_HotelAvailRS", {})
            .get("RoomStays", {})
            .get("RoomStay", {})
            .get("RoomTypes", {})
            .get("RoomType", [])
    )
 
 
    room_types = ensure_list(room_types)

    rows = []

    for room_type in room_types:
        room_type_code = (
            room_type.get("@RoomTypeCode")
            or room_type.get("RoomTypeCode")
            or ""
        )

        room_type_name = (
            room_type.get("RoomDescription", {}).get("@Name")
            or room_type.get("@RoomTypeName")
            or room_type.get("RoomTypeName")
            or room_type.get("Name")
            or ""
        )

        rows.append({
            "room_type_code": room_type_code,
            "room_type_name": room_type_name,
            "data": json.dumps(room_type, ensure_ascii=False)
        })

    return rows


def extract_rate_plans_from_response(data):
    rate_plans = (
        data.get("data", {})
            .get("s:Envelope", {})
            .get("s:Body", {})
            .get("OTA_HotelAvailRS", {})
            .get("RoomStays", {})
            .get("RoomStay", {})
            .get("RatePlans", {})
            .get("RatePlan", [])
    )
 
 
    rate_plans = ensure_list(rate_plans)

    rows = []

    for rate_plan in rate_plans:
        rate_plan_code = (
            rate_plan.get("@RatePlanCode")
            or rate_plan.get("RatePlanCode")
            or ""
        )

        rate_plan_name = (
            rate_plan.get("RatePlanDescription", {}).get("@Name")
            or rate_plan.get("@RatePlanName")
            or rate_plan.get("RatePlanName")
            or rate_plan.get("Name")
            or ""
        )
        
        availability_block =(
            rate_plan.get("@InvBlockCode")
            or rate_plan.get("InvBlockCode")
            or ""
        )
        allow_upload_price =(
            rate_plan.get("@PriceUploadIsAllowed")
            or rate_plan.get("PriceUploadIsAllowed")
            or False
        )

        

      
        rows.append({
            "rate_plan_code": rate_plan_code,
            "rate_plan_name": rate_plan_name,
            "availability_block":availability_block,
            "allow_upload_price": True if str(allow_upload_price).lower() == 'true' else False
        })
       

    return [d for d in rows if d.get("allow_upload_price")]
    
def extract_payment_types_from_response(data):
    payment_types = (
        data.get("data", {})
            .get("s:Envelope", {})
            .get("s:Body", {})
            .get("OTA_HotelAvailRS", {})
            .get("RoomStays", {})
            .get("RoomStay", {})
            .get("Guarantee", {}) 
    ) 
 
    
    payment_types = ensure_list(payment_types)

    rows = []
 
    for payment_type in payment_types:
        payment_t = payment_type["Comments"]["Comment"]

        # Get payment type code
        payment_type_code = next(
            (pt.get("Text") for pt in payment_t if pt.get("@Name") == "PaymentSystemCode"),
            None
        )   
        
        # Get payment type name
        payment_type_title = next(
            (pt.get("Text") for pt in payment_t if pt.get("@Name") == "PaymentSystemTitle"),
            None
        ) 
        
        # Get payment type title  
        payment_type_name = next(
            (pt.get("Text") for pt in payment_t if pt.get("@Name") == "PaymentSystemName"),
            None
        )    

        rows.append({
            "payment_type_code": payment_type_code,
            "payment_type_name": payment_type_name,
            "payment_type_title": payment_type_title
        })

    return rows

def extract_service_from_response(data):
    service = (
        data.get("data", {})
            .get("s:Envelope", {})
            .get("s:Body", {})
            .get("OTA_HotelAvailRS", {})
            .get("Services", {})
            .get("Service", {})
    )
     
    service = ensure_list(service)

    rows = []

    for s in service:
        service_code = s["@ID"] 

        get_service_name = s["ServiceDetails"]["Comments"]["Comment"]

        service_name = next(
            (sv.get("Text") for sv in get_service_name if sv.get("@Name") == "ServiceName"),
            None
        )   

        rows.append({
            "services_code": service_code,
            "service_name": service_name
        })

    return rows


@frappe.whitelist()
def test(property):
    config = get_exely_config(property)

    body_content = f"""
    <OTA_HotelAvailRQ xmlns="http://www.opentravel.org/OTA/2003/05" Version="1.17">
        <AvailRequestSegments>
            <AvailRequestSegment>
                <HotelSearchCriteria>
                    <Criterion>
                        <HotelRef HotelCode="{config['hotel_code']}"/>
                    </Criterion>
                </HotelSearchCriteria>
            </AvailRequestSegment>
        </AvailRequestSegments>
    </OTA_HotelAvailRQ>
    """

    data = send_soap_request(property, "OTA_HotelAvailRQ", body_content)
    services = extract_payment_types_from_response(data)


    return data
 
def content_body(property):
    config = get_exely_config(property)

    body_content = f"""
    <OTA_HotelAvailRQ xmlns="http://www.opentravel.org/OTA/2003/05" Version="1.17">
        <AvailRequestSegments>
            <AvailRequestSegment>
                <HotelSearchCriteria>
                    <Criterion>
                        <HotelRef HotelCode="{config['hotel_code']}"/>
                    </Criterion>
                </HotelSearchCriteria>
            </AvailRequestSegment>
        </AvailRequestSegments>
    </OTA_HotelAvailRQ>
    """

    data = send_soap_request(property, "OTA_HotelAvailRQ", body_content)
    room_types = extract_room_types_from_response(data)
    rate_plans = extract_rate_plans_from_response(data)
    payment_types = extract_payment_types_from_response(data)
    services = extract_service_from_response(data)

    return room_types, rate_plans, payment_types, services


@frappe.whitelist()
def send_property_info(property):
    room_types, rate_plans, payment_types, services = content_body(property)
    return {
        "room_types": room_types,
        "rate_plans": rate_plans,
        "payment_types": payment_types,
        "services": services
    }



