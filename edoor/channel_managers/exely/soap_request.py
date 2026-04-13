import frappe
import requests
import xmltodict
import json
from edoor.channel_managers.exely.error_code import EXELY_ERROR_CODES
# Constants
SOAP_HEADER_NAMESPACE = "https://www.hopenapi.com/Api/PMSConnect" 
REQUEST_TIMEOUT = 30


OTA_REQUEST = {
    "OTA_HotelAvailNotifRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelAvailNotifRQ",
        "response_key":"OTA_HotelAvailNotifRS"
    },
    "OTA_HotelAvailRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelAvailRQ",
        "response_key":"OTA_HotelAvailRS"
    },
    "OTA_ReadRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelReadReservationRQ",
        "response_key":"OTA_ReadRS"
        # Get Booking From exely
    },
    "OTA_NotifReportRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/NotifReportRQRequest",
        "response_key":"OTA_NotifReportRS"
        # The Confirmation Message
    },
    "OTA_HotelRateAmountNotifRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelRateAmountNotifRQ",
        "response_key":"OTA_HotelRateAmountNotifRS"
        # The Confirmation Message
    }


}

def get_exely_config(property):
    channel = frappe.get_cached_doc("Channel Manager Integration",property)
    config = {
        "username": channel.username,
        "password": channel.password,
        "url": channel.api_url,
        "hotel_code": channel.property_code,
        "docname": channel.name,
        "property": channel.property
    }
    return config


def request_soap_action(property, ota_request, body):
    config = get_exely_config(property)
    headers = {
        "SOAPAction": OTA_REQUEST.get(ota_request).get("SOAPAction"),
        "Content-Type": "text/xml"
    }
    response = requests.post(
        f"{config['url']}?HotelCode={config['hotel_code']}",
        headers=headers,
        data=body,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()
    data = xmltodict.parse(response.text)
    return data


def build_soap_body(property, body_content):
    config = get_exely_config(property)
    body = f"""
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Header xmlns="{SOAP_HEADER_NAMESPACE}">
            <Security Username="{config['username']}" Password="{config['password']}" />
        </soap:Header>
        <soap:Body>
            {body_content}
        </soap:Body>
    </soap:Envelope>
    """

    return body



def send_soap_request(property, ota_request, body_content):
    soap_body = build_soap_body(property, body_content)
    response_data = request_soap_action(property, ota_request, soap_body)
    resp = soap_response_status(ota_request,response_data)
    resp["data"] = response_data
    return resp



def soap_response_status(ota_request,data):
    """
    Check if OTA SOAP response contains Success element
    Return True if success, False otherwise
    """
    

    

    resp = data.get("s:Envelope", {}).get("s:Body", {}).get(OTA_REQUEST.get(ota_request).get("response_key"), {})
    status = ""
    if "Success" in resp:
        status = "Success"
    if "Warnings" in resp:
        status ="Warning"

    if "Errors" in resp:
        success ="Fail"
    def get_warning_text():
        warnings = []
        if "Warnings" in resp:
            for w in resp.get("Warnings",{}).get("Warning"):
                
                warnings.append(f"{w.get('@Code')} - {w.get('#text')}")

        return warnings or []

    def get_error_text():
        errors = []
        if "Errors" in resp:
            for w in resp.get("Errors",{}).get("Error"):
                errors.append(f"{w.get('@Code')} - {w.get('#text')}")
        return errors or []
        

    def get_priority_error_code():
        codes = [d.get("@Code") for d in   resp.get("Errors",{}).get("Error") or []]
        codes.extend([d.get("@Code") for d in   resp.get("Warnings",{}).get("Warning") or []] )
        error_codes = []
        for c in codes:
            err = EXELY_ERROR_CODES.get(c)
            if err and err.get("priority"):
                error_codes.append(err)
        if error_codes:
            return min(error_codes, key=lambda x: x["priority"])
        return None
        




    warnings  = get_warning_text()
    errors  = get_error_text()
    response_text = "\n".join(warnings + errors)
      

    data ={
        "status":status,
        "warning_text":  "\n".join(warnings),
        "error_text":  "\n".join(errors),
        "response_text":response_text,
        "error_code": get_priority_error_code()
    }

    return data

 


@frappe.whitelist()
def test_me():
  
 
    data  = {
    "s:Envelope": {
        "@xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
        "s:Body": {
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "OTA_HotelRateAmountNotifRS": {
                "@Version": "1.17",
                "@xmlns": "http://www.opentravel.org/OTA/2003/05",
                "Warnings": {
                    "Warning": [
                        {
                            "@Language": "EN",
                            "@Type": "3",
                            "@Code": "135",
                            "@Tag": "/OTA_HotelRateAmountNotifRQ/RateAmountMessages/RateAmountMessage[1]",
                            "#text": 'End date was truncated to 13.04.2028, InvTypeCode="5001574", RatePlanCode="10003870"'
                        },
                        {
                            "@Language": "EN",
                            "@Type": "3",
                            "@Code": "852",
                            "@Tag": "/OTA_HotelRateAmountNotifRQ/RateAmountMessages/RateAmountMessage[1]/Rates/Rate[1]/AdditionalGuestAmounts/AdditionalGuestAmount[1]",
                            "#text": 'Child bed category was not found MinAge="15" MaxAge="20", InvTypeCode="5001574", RatePlanCode="10003870"'
                        },
                        {
                            "@Language": "EN",
                            "@Type": "3",
                            "@Code": "505",
                            "@Tag": "/OTA_HotelRateAmountNotifRQ/RateAmountMessages/RateAmountMessage[1]/Rates/Rate[2]/BaseByGuestAmts/BaseByGuestAmt[1]@NumberOfGuests",
                            "#text": 'Adult bed was not found NumberOfGuests="8", InvTypeCode="5001574", RatePlanCode="10003870"'
                        },
                        {
                            "@Language": "EN",
                            "@Type": "3",
                            "@Code": "505",
                            "@Tag": "/OTA_HotelRateAmountNotifRQ/RateAmountMessages/RateAmountMessage[1]/Rates/Rate[2]/BaseByGuestAmts/BaseByGuestAmt[2]@NumberOfGuests",
                            "#text": 'Adult bed was not found NumberOfGuests="9", InvTypeCode="5001574", RatePlanCode="10003870"'
                        }
                    ]
                },
                "Success": {}
            }
        }
    }
}
    return soap_response_status("OTA_HotelRateAmountNotifRQ",data)



