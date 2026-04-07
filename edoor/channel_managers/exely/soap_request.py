import frappe
import requests
import xmltodict
import json

# Constants
SOAP_HEADER_NAMESPACE = "https://www.hopenapi.com/Api/PMSConnect" 
REQUEST_TIMEOUT = 30


OTA_REQUEST = {
    "OTA_HotelAvailNotifRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelAvailNotifRQ"
    },
    "OTA_HotelAvailRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelAvailRQ"
    },
    "OTA_ReadRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelReadReservationRQ"
        # Get Booking From exely
    },
    "OTA_NotifReportRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/NotifReportRQRequest"
        # The Confirmation Message
    },
    "OTA_HotelRateAmountNotifRQ":{
        "SOAPAction":"https://www.hopenapi.com/Api/PMSConnect/HotelRateAmountNotifRQ"
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
    return {
        "status": soap_response_status(response_data),
        "data": response_data,
        "response_text":frappe.as_json(response_data) # create python to get frienly response text
    }

def soap_response_status(data):
    """
    Check if OTA SOAP response contains Success element
    Return True if success, False otherwise
    """

    try:
        resp = data.get("s:Envelope", {}).get("s:Body", {}).get("OTA_HotelAvailNotifRS", {})

        if "Success" in resp:
            return True

        return False

    except Exception:
        return False



