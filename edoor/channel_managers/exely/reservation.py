
import email
import email
import json
import frappe
import xmltodict
from datetime import datetime
from .soap_request import get_exely_config, send_soap_request
from .utils import random_color,get_room_type_mapping,get_country,create_guest
from edoor.api.reservation import add_new_reservation

@frappe.whitelist()
def get_hotel_bookings():
    config = get_exely_config()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    body = f"""
            <OTA_ReadRQ xmlns="http://www.opentravel.org/OTA/2003/05"
                        Version="1.17"
                        TimeStamp="{timestamp}">
                <ReadRequests>
                    <HotelReadRequest HotelCode="{config['hotel_code']}">
                        <SelectionCriteria SelectionType="Undelivered"/>
                    </HotelReadRequest>
                </ReadRequests>
            </OTA_ReadRQ>
    """
    data = send_soap_request("OTA_ReadRQ", body)
    return data
@frappe.whitelist()
def map_exely_to_reservation(exely_json):
    exely_json = exely_json.get("data", {})
    res_body = exely_json.get("s:Envelope", {}).get("s:Body", {})
    ota_res = res_body.get("OTA_ResRetrieveRS", {})

    hotel_res = ota_res.get("ReservationsList", {}).get("HotelReservation", [])

    # ensure list
    if isinstance(hotel_res, dict):
        hotel_res = [hotel_res]
    config = get_exely_config()
    property = config.get("property")
    edoor_setting = frappe.get_cached_doc("eDoor Setting")
    reservations = []

    for res in hotel_res:

        # --------------------------
        # Guest Info
        # --------------------------
        master_guest_info_data = res.get("ResGlobalInfo", {}).get("Profiles", {}).get("ProfileInfo", {})
        phone = ""
        email = ""
        gender = "Not Set"
        guest_full_name = ""

        if isinstance(master_guest_info_data.get("Profile"), dict):

            customer = master_guest_info_data["Profile"].get("Customer", {})

            person_name = customer.get("PersonName", {})
            country = customer.get("CitizenCountryName", {}).get("@Code", "")

            given = person_name.get("GivenName", "")
            middle = person_name.get("MiddleName", "")
            surname = person_name.get("Surname", "")

            guest_full_name = " ".join(
    [x for x in [given, middle, surname] if x]
)

            phone = customer.get("Telephone", {}).get("@PhoneNumber", "")
            email = customer.get("Email", "")

            gender = "Not Set" if customer.get("@Gender") == "Unknown" else customer.get("@Gender", "Not Set")

        # --------------------------
        # Stay Guest Info
        # --------------------------
        res_guests = res.get("ResGuests", {}).get("ResGuest", [])
        if isinstance(res_guests, dict):
            res_guests = [res_guests]

        guest_map = {
            str(g.get("@ResGuestRPH")): g.get("Profiles", {})
                .get("ProfileInfo", {})
                .get("Profile", {})
                .get("Customer", {})
            for g in res_guests
        }
        # --------------------------
        # RoomStays
        # --------------------------
        room_stays_raw = res.get("RoomStays", {}).get("RoomStay", [])

        if isinstance(room_stays_raw, dict):
            room_stays_raw = [room_stays_raw]

        reservation_stays = []

        total_adult = 0
        total_child = 0
        total_amount = 0

        for rs in room_stays_raw:

            guest_counts = rs.get("GuestCounts", {}).get("GuestCount", [])

            if isinstance(guest_counts, dict):
                guest_counts = [guest_counts]

            adult_count = 0
            child_count = 0
            stay_guest_docs = []
            additional_guest_docs = []
            is_first_rph = True
            for i, g in enumerate(guest_counts):
                age_code = g.get("@AgeQualifyingCode")
                count = int(g.get("@Count", 0))

                if age_code in ("AdultBed", "AdultExtraBed"):
                    adult_count += count
                elif age_code in ("ChildBandBed", "ChildBandExtraBed", "ChildBandWithoutBed"):
                    child_count += count

                guest_info = guest_map.get(str(g.get("@ResGuestRPH")), {})

                country_data = get_country(
                    guest_info.get("CitizenCountryName", {}).get("@Code", "")
                ) or {}

                guest_data = {
                    "guest_name": (
                        guest_info.get("PersonName", {}).get("GivenName", "") + " " +
                        guest_info.get("PersonName", {}).get("Surname", "")
                    ).strip(),
                    "nationality": country_data.get("name", "")
                }
                if g.get("@ResGuestRPH") and is_first_rph:
                    stay_guest_docs.append(create_guest(guest_data))
                    is_first_rph = False
                elif g.get("@ResGuestRPH"):
                    additional_guest_docs.append(create_guest(guest_data))



            total_child += child_count
            total_adult += adult_count

            total_rs_amount = float(rs.get("Total", {}).get("@AmountAfterTax", 0))
            total_amount += total_rs_amount

            room_type_id = rs.get("RoomTypes", {}).get("RoomType", {}).get("@RoomTypeCode", "")
            room_type = get_room_type_mapping(room_type_id,property)
            if not room_type:
                frappe.log_error(f"Room type with code {room_type_id} not found in mapping", "Exely Room Type Mapping")
                return 
            reservation_stays.append({
                "rate": total_rs_amount,
                "adult": adult_count,
                "child": child_count,
                "is_manual_rate": 0,
                "is_master": 0,
                "room_type_id":room_type.get("edoor_room_type", ""),
                "room_id": "",
                "guest": stay_guest_docs[0].name or None,
                "guest_name": stay_guest_docs[0].customer_name_en or None,
                "guest_phone_number": stay_guest_docs[0].guest_phone_number or None,
                "guest_email": stay_guest_docs[0].guest_email or None,
                "nationality": stay_guest_docs[0].nationality or None,
                "guest_type": stay_guest_docs[0].guest_type or None
                
            })




        # --------------------------
        # TimeSpan
        # --------------------------
        time_span = res.get("ResGlobalInfo", {}).get("TimeSpan", {})
        
        arrival_date = time_span.get("@Start", "")
        departure_date = time_span.get("@End", "")
        room_night = time_span.get("@Duration", "")

        # --------------------------
        # Reservation Info
        # --------------------------
        reservation_date = res.get("@CreateDateTime", "")
        unique_id = res.get("UniqueID", {})
        channel_manager_booking_id = unique_id.get("@ID", "")
        unique_type = unique_id.get("@Type", "")
        creation = res.get("@CreateDateTime", "")
        modified = res.get("@ModifyDateTime", "")
        group_color = random_color()
        existing_guest = None
        if email:
            existing_guest = frappe.db.exists("Customer", {"email_address": email})
            master_guest_info = frappe.get_doc("Customer", existing_guest)
            master_guest_info.gender = gender
            master_guest_info.customer_group = "General"
            master_guest_info.customer_name_en = guest_full_name
            master_guest_info.customer_name_kh = guest_full_name
            master_guest_info.phone_number = phone
            master_guest_info.email_address = email
        else:
            master_guest_info = {
                "doctype": "Customer",
                "gender": gender,
                "customer_group": "General",
                "customer_name_en": guest_full_name,
                "customer_name_kh": guest_full_name,
                "phone_number": phone,
                "email_address": email
            }
            
            
            
        mapped = {
            "doc": {
                "reservation": {
                    "doctype": "Reservation",
                    "property": property,
                    "reference_number": channel_manager_booking_id,
                    "reservation_type": "FIT",
                    "arrival_time": edoor_setting.default_check_in_time or "12:00:00",
                    "departure_time": edoor_setting.default_check_out_time or "12:00:00",
                    "adult": total_adult,
                    "child": total_child,
                    "reservation_status": res.get("@ResStatus"),
                    "channel_manager_booking_id": channel_manager_booking_id,
                    "group_code": "",
                    "group_name": "",
                    "show_room_rate_in_guest_folio_invoice": 1,
                    "auto_assign_room": False,
                    "reservation_color_code": "",
                    "group_color": group_color,
                    "allow_post_to_city_ledger": 1,
                    "reservation_date": reservation_date,
                    "arrival_date": arrival_date,
                    "departure_date": departure_date,
                    "room_night": room_night,
                    "business_source_type": "OTA",
                    "business_source": "Test Source",
                    "business_source_type_group": "Direct",
                    "rate_type": "Daily Rate",
                    "paid_by_master_room": 1,
                    "tax_1_rate": 5,
                    "tax_2_rate": 2,
                    "tax_3_rate": 10,
                    "rate_include_tax": "Yes",
                    "guest":existing_guest or ""
                    
                },

                "guest_info": master_guest_info,
                "reservation_stay": reservation_stays,
                "additional_guests": additional_guest_docs,
                "tax_rule": {
                    "rate_include_tax": "Yes",
                    "tax_1_rate": 5,
                    "tax_2_rate": 2,
                    "tax_3_rate": 10
                },

                "allow_user_to_edit_rate": 1,
                "is_package": 0,
                "package_charge_data": "[]",
                "is_house_use": 0,
                "is_complimentary": 0
            }
        }
    
        reservations.append(mapped)

    return reservations

def confirmation_message(data):
    reservation_xml_list = []

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    config = get_exely_config()
    hotel_code = config.get("hotel_code")

    for d in data:
        unique_id = d.get("channel_manager_booking_id", "")
        pms_id = d.get("pms_id", "")

        if pms_id:
            body = f"""
            <HotelReservation CreateDateTime="{now}" LastModifyDateTime="{now}" ResStatus="Reserved">
                <UniqueID Type="14" ID="{unique_id}" />
                <ResGlobalInfo>
                    <HotelReservationIDs>
                        <HotelReservationID ResID_Type="14" ResID_Value="{pms_id}" />
                    </HotelReservationIDs>
                </ResGlobalInfo>
            </HotelReservation>
            """
        else:
            body = f"""
            <HotelReservation CreateDateTime="{now}" LastModifyDateTime="{now}" ResStatus="RequestDenied">
                <UniqueID Type="14" ID="{unique_id}" />
                <ResGlobalInfo>
                    <Comments>
                        <Comment>
                            <Text>Unable to save in PMS (eDoor)</Text>
                        </Comment>
                    </Comments>
                </ResGlobalInfo>
            </HotelReservation>
            """

        reservation_xml_list.append(body.strip())

    all_reservations = "\n".join(reservation_xml_list)

    main_body = f"""
<OTA_NotifReportRQ xmlns="http://www.opentravel.org/OTA/2003/05" Version="1.17" EchoToken="echo">
    <Success/>
    <NotifDetails HotelCode="{hotel_code}">
        <HotelNotifReport>
            <HotelReservations>
                {all_reservations}
            </HotelReservations>
        </HotelNotifReport>
    </NotifDetails>
</OTA_NotifReportRQ>
""".strip()
    return send_soap_request("OTA_NotifReportRQ", main_body)
# add new reservation from exely to edoor
@frappe.whitelist()
def add_new_exely_bookings():
    # booking = get_hotel_bookings()
    booking = {"status":0,"data":{"s:Envelope":{"@xmlns:s":"http://schemas.xmlsoap.org/soap/envelope/","s:Body":{"@xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance","@xmlns:xsd":"http://www.w3.org/2001/XMLSchema","OTA_ResRetrieveRS":{"@Version":"1.17","@xmlns":"http://www.opentravel.org/OTA/2003/05","ReservationsList":{"HotelReservation":{"@CreateDateTime":"2026-03-11T07:50:43.433","@LastModifyDateTime":"2026-03-18T07:39:25.523","@ResStatus":"Confirmed","POS":{"Source":{"RequestorID":{"@Type":"22","@ID":"PMSConnect"},"BookingChannel":{"@Type":"7","TPA_Extensions":{"BookingWebSource":{"@Code":"","@Url":"https://booking.exely.com/qa/?hotel=501674"}}}}},"UniqueID":{"@Type":"14","@ID":"20260406-501674-1200385334"},"RoomStays":{"RoomStay":{"@IndexNumber":"0","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001575","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":[{"@RatePlanID":"10003870"},{"@RatePlanID":"10003541"}]},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-06","@ExpireDate":"2026-04-06","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"230.0000","@AmountAfterTax":"230.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-07","@ExpireDate":"2026-04-07","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"230.0000","@AmountAfterTax":"230.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"1"},{"@AgeQualifyingCode":"AdultExtraBed","@Count":"1","@ResGuestRPH":"2"}]},"TimeSpan":{"@Start":"2026-04-06T14:00:00","@Duration":"2","@End":"2026-04-08T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-05T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"230"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"460.0000","@AmountAfterTax":"460.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}}},"ResGuests":{"ResGuest":[{"@ResGuestRPH":"1","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200431302","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Rathana","MiddleName":"","Surname":"Tes"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"2","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200431303","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Dara","MiddleName":"","Surname":"Tes"},"CitizenCountryName":{"@Code":"GBR"}}}}}}]},"ResGlobalInfo":{"TimeSpan":{"@Start":"2026-04-06T14:00:00","@Duration":"2","@End":"2026-04-08T12:00:00"},"Comments":{"Comment":{"Text":"Guest's comment: my requestr detail"}},"Guarantee":{"@GuaranteeCode":"None","Comments":{"Comment":[{"@Name":"PaymentMethodName","Text":"PayOnArrival"},{"@Name":"PaymentSystemName","Text":"AT_ARRIVAL"},{"@Name":"PaymentSystemCode","Text":"5003924"},{"@Name":"PaymentSystemTitle","Text":"At check-in"}]}},"Total":{"@AmountBeforeTax":"710.0000","@AmountAfterTax":"710.0000","@CurrencyCode":"USD"},"Profiles":{"ProfileInfo":{"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Lak","MiddleName":"","Surname":"Heng"},"Telephone":{"@PhoneNumber":"+85545879658"},"Email":"lakleabhengteasting@gamil.com"}}}}},"Services":{"Service":{"@ServicePricingType":"Per stay","@ServiceRPH":"1","@Inclusive":"false","@Quantity":"1","@ID":"5002979","ServiceDetails":{"TimeSpan":{"@Start":"2026-04-06T00:00:00","@Duration":"1"},"Comments":{"Comment":{"@Name":"Test Service","Text":"test services desition"}},"Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}}}}}},"Success":0}}}}}
    data = map_exely_to_reservation(booking)
    booking_confirmation = []
    return booking
    if data:
        for d in data:
            edoor_data = add_new_reservation(
                    d.get("doc"),
                    sync_room_available_to_channel_manager=False
                )
            try:
                # edoor_data = add_new_reservation(
                #     d.get("doc"),
                #     sync_room_available_to_channel_manager=False
                # )
                if(edoor_data):
                    booking_confirmation.append({
                        "channel_manager_booking_id": d.get("doc").get("reservation").get("channel_manager_booking_id"),
                        "pms_id": edoor_data.get("name", ""),
                        "status": "Success"
                    })

            except Exception as e:
                booking_confirmation.append({
                    "channel_manager_booking_id": d.get("doc").get("reservation").get("channel_manager_booking_id"),
                    "pms_id":"",
                    "status": "Failed",
                    "error": str(e)
                })
        return booking_confirmation
        # if booking_confirmation:
        #     confirmation_message(booking_confirmation)
        # frappe.enqueue(
        #         "edoor.channel_managers.exely.availability.update_room_availability",
        #         queue="channel_manager",
        #         property="ESTC HOTEL 6"
        #     )
        
    else:
        frappe.log_error("No new bookings to add from Exely", "Exely Booking Sync")