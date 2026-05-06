
import email
import json
import frappe
import xmltodict
from datetime import datetime,timedelta
from .soap_request import get_exely_config, send_soap_request
from .utils import *
from edoor.api.reservation import add_new_reservation

@frappe.whitelist()
def get_hotel_bookings(property):
    config = get_exely_config(property)
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
    data = send_soap_request(property,"OTA_ReadRQ", body)
    return data
@frappe.whitelist()
def map_exely_to_reservation(exely_json, property):
    exely_json = exely_json.get("data", {})
    res_body = exely_json.get("s:Envelope", {}).get("s:Body", {})
    ota_res = res_body.get("OTA_ResRetrieveRS", {})

    hotel_res = ota_res.get("ReservationsList", {}).get("HotelReservation", [])

    # ensure list
    if isinstance(hotel_res, dict):
        hotel_res = [hotel_res]
    config = get_exely_config(property)
    property = config.get("property")
    edoor_setting = frappe.get_cached_doc("eDoor Setting")
    reservations = []
    
    for res in hotel_res:
        # --------------------------
        # TimeSpan
        # --------------------------
        time_span = res.get("ResGlobalInfo", {}).get("TimeSpan", {})
        arrival_date = time_span.get("@Start", "")
        departure_date = time_span.get("@End", "")
        room_night = time_span.get("@Duration", "")
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
        # Service Info
        # --------------------------
        service_item = ensure_list(res.get("Services", {}).get("Service"))
        service_mapping = {
            str(g.get("@ServiceRPH")): g
            for g in service_item
        }
        # services with inventory code 'Transfer'
        transfer_services = [
            g for g in service_item if g.get("@ServiceInventoryCode") == "Transfer"
        ]
        # --------------------------
        # RoomStays
        # --------------------------
        
        room_stays_raw = ensure_list(res.get("RoomStays", {}).get("RoomStay"))

        reservation_stays = []

        total_adult = 0
        total_child = 0
        total_amount = 0
        grouped = {}
        for idx, rs in enumerate(room_stays_raw):
            is_master = 0
            paid_by_master_room = 1
            pick_up_drop_off_info = []
            child_list = []
            adult_count = 0
            adult_bed_count = []
            child_count = 0
            stay_guest_docs = []
            additional_guest_docs = []
            is_first_rph = True
            guest_counts = ensure_list(rs.get("GuestCounts", {}).get("GuestCount"))
            for i, g in enumerate(guest_counts):
                age_code = g.get("@AgeQualifyingCode")
                count = int(g.get("@Count", 0))
                age = int(g.get("@Age", 0))
                age_bucket = int(g.get("@AgeBucket", 0))
                key = (age_code, age_bucket)
                is_alult = 0

                if age_code in ("AdultBed", "AdultExtraBed"):
                    is_alult = 1
                    adult_count += count
                elif "Child" in str(age_code):
                    child_count += count
                if key not in grouped:
                    grouped[key] = {
                        "@AgeQualifyingCode": age_code,
                        "@AgeBucket": age_bucket,
                        "@Age": [],
                        "@Count": 0,
                        "is_alult": is_alult
                    }
                if age is not None:
                    grouped[key]["@Age"].append(str(age))
                grouped[key]["@Count"] += int(g.get("@Count", 0))
                
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
            child_list.extend(add_guest_list(grouped))
            # frappe.throw(str(guest_counts))
            # frappe.throw(str(grouped))
            total_child += child_count
            total_adult += adult_count

            total_rs_amount = float(rs.get("Total", {}).get("@AmountAfterTax") or 0)
            total_amount += total_rs_amount
            service_rphs = ensure_list(rs.get("ServiceRPHs", {}).get("ServiceRPH"))
            service_info = []
            for s in service_rphs:
                service_data = service_mapping.get(str(s.get("@RPH")), {})
                
                package = get_package_rule_mapping(str(service_data.get("@ServicePricingType")),property)
                description = (
                    (service_data.get("ServiceDetails") or {})
                    .get("Comments", {})
                    .get("Comment", {})
                )
                rate = (
                        (service_data.get("ServiceDetails") or {})
                        .get("Total", {})
                        .get("@AmountBeforeTax", 0)
                    )
                
                account_code = get_service_mapping(service_data.get("@ID"),property)
                
                account_code = account_code.get("edoor_service_code") if account_code else ""
                service_info.append({
                    "account_code":account_code  ,
                    "charge_rule": package.get("edoor_charge_rule", "") if package else "",
                    "posting_rule": package.get("edoor_posting_rule", "") if package else "",
                    "is_inclusive": 1 if service_data.get("@Inclusive") == "true" else 0,
                    "description":(description or {}).get("Text", ""),
                    "rate":rate
                
                })
            if idx == 0:
                is_master = 1
                paid_by_master_room = 1
                if transfer_services:
                    for transfer in transfer_services:
                        
                        start_raw = (
                            (transfer.get("ServiceDetails") or {})
                            .get("TimeSpan", {})
                            .get("@Start")
                        )

                        start_date = datetime.fromisoformat(start_raw).date() if start_raw else None
                        arrival_date_only = datetime.fromisoformat(arrival_date).date() if arrival_date else None
                        departure_date_only = datetime.fromisoformat(departure_date).date() if departure_date else None

                        rate = (
                            (transfer.get("ServiceDetails") or {})
                            .get("Total", {})
                            .get("@AmountBeforeTax", 0)
                        )
                        description = (
                            (transfer.get("ServiceDetails") or {})
                            .get("Comments", {})
                            .get("Comment", {})
                        )
                        package = get_package_rule_mapping(str(transfer.get("@ServiceInventoryCode")),property)
                        account_code = get_service_mapping(transfer.get("@ID"),property)
                        if account_code:
                            account_code = account_code.get("edoor_service_code")
                        pick_up = {}
                        drop_off = {}

                        if start_date == arrival_date_only:
                            pick_up_info = parse_transfer((description or {}).get("Text", ""))
                            # pick_up_info.get("mode")
                            # pick_up_info.get("route")
                            pick_up = {
                                "require_pickup": 1,
                                "pickup_time": pick_up_info.get("time"),
                                "arrival_mode": "",
                                "arrival_flight_number": pick_up_info.get("flight_number"),
                                "pickup_location": "",
                                "pickup_note": (description or {}).get("Text", ""),
                                "pickup_rate": pick_up_info.get("amount"),

                            }
                        elif start_date in [departure_date_only, departure_date_only + timedelta(days=1)]:
                            drop_off_info = parse_transfer((description or {}).get("Text", ""))
                            # drop_off_info.get("mode")
                            # drop_off_info.get("route")
                            drop_off = {
                                "require_drop_off": 1,
                                "drop_off_time": drop_off_info.get("time"),
                                "departure_mode": "",
                                "departure_flight_number": drop_off_info.get("flight_number"),
                                "drop_off_location": "",
                                "drop_off_note": (description or {}).get("Text", ""),
                                "drop_off_rate": drop_off_info.get("amount"),


                            }
                            
                        
                        if pick_up:
                            pick_up_drop_off_info.append(pick_up)
                        if drop_off:
                            pick_up_drop_off_info.append(drop_off)
                        service_info.append({
                        "account_code":account_code  ,
                        "charge_rule": package.get("edoor_charge_rule", "") if package else "",
                        "posting_rule": package.get("edoor_posting_rule", "") if package else "",
                        "is_inclusive": 1 if transfer.get("@Inclusive") == "true" else 0,
                        "description":(description or {}).get("Text", ""),
                        "rate":rate
                    
                    })
            #  room type mapping
            room_type_id = rs.get("RoomTypes", {}).get("RoomType", {}).get("@RoomTypeCode", "")
            room_type = get_room_type_mapping(room_type_id,property)
            if not room_type:
                frappe.log_error(f"Room type with code {room_type_id} not found", "Exely Mapping")
                continue
            
            room_rate_raw = rs.get("RoomRates", {}).get("RoomRate") or {}
            if isinstance(room_rate_raw, dict):
                room_rate_raw = [room_rate_raw]
                
            # room_rate_list = []
            # for rate in room_rate_raw:
            #     rate_type = get_rate_type_mapping(rate.get("@RatePlanCode"),property)
            #     room_rate_list.append({
            #         "rate_type": rate_type.get("edoor_rate_plan", "") if rate_type else "",
            #         "input_rate": float(rate.get("Total", {}).get("@AmountBeforeTax", 0)),
            #         "date": rate.get("@EffectiveDate")
            #     })
            # room rate and guest info for each stay
            # frappe.throw(str(service_info))
            stay_data = {
                "rate": total_rs_amount,
                "adult": adult_count,
                "child": child_count,
                "is_manual_rate": 0,
                "is_master": is_master,
                "room_type_id": room_type.get("edoor_room_type", ""),
                "room_id": "",
                "paid_by_master_room":paid_by_master_room,
                "guest": stay_guest_docs[0].name if stay_guest_docs else None,
                "guest_name": stay_guest_docs[0].customer_name_en if stay_guest_docs else None,
                "guest_phone_number": stay_guest_docs[0].guest_phone_number if stay_guest_docs else None,
                "guest_email": stay_guest_docs[0].guest_email if stay_guest_docs else None,
                "nationality": stay_guest_docs[0].nationality if stay_guest_docs else None,
                "guest_type": stay_guest_docs[0].guest_type if stay_guest_docs else None,
                "package_items": service_info,
                "additional_guests": additional_guest_docs,
                "child_list":child_list
            }
            merged_transfer = {}
            if pick_up_drop_off_info:
                for item in pick_up_drop_off_info:
                    if isinstance(item, dict):
                        merged_transfer.update(item)
            
                stay_data.update(merged_transfer)
            
            reservation_stays.append(stay_data)
  
        


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
        existing_guest = frappe.db.exists("Customer", {"email_address": email})
        if existing_guest:
            master_guest_info = frappe.get_doc("Customer", existing_guest)
            master_guest_info.gender = gender
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
        
        # comment 
        note = res.get("ResGlobalInfo", {}).get("Comments", {}).get("Comment", {}).get("Text", "")   
        # room rate

        # payment method
        # 

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
                    "paid_by_master_room":1,
                    "reservation_date": reservation_date,
                    "arrival_date": arrival_date,
                    "departure_date": departure_date,
                    "room_night": room_night,
                    "business_source_type": "OTA",
                    "business_source": "Test Source",
                    "business_source_type_group": "Direct",
                    "rate_type": "Daily Rate",
                    "tax_1_rate": 5,
                    "tax_2_rate": 2,
                    "tax_3_rate": 10,
                    "rate_include_tax": "Yes",
                    "guest":existing_guest or "",
                    "note": note
                    
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

def confirmation_message_booking(data,property):
    reservation_xml_list = []

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    config = get_exely_config(property)
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
    return send_soap_request(property,"OTA_NotifReportRQ", main_body)
# add new reservation from exely to edoor
@frappe.whitelist()
def add_new_exely_bookings(property="ESTC HOTEL 6"):
    booking = get_hotel_bookings(property)
    # booking = {"status":0,"data":{"s:Envelope":{"@xmlns:s":"http://schemas.xmlsoap.org/soap/envelope/","s:Body":{"@xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance","@xmlns:xsd":"http://www.w3.org/2001/XMLSchema","OTA_ResRetrieveRS":{"@Version":"1.17","@xmlns":"http://www.opentravel.org/OTA/2003/05","ReservationsList":{"HotelReservation":{"@CreateDateTime":"2026-03-25T05:44:19.513","@LastModifyDateTime":"2026-03-27T05:15:25.147","@ResStatus":"Confirmed","POS":{"Source":{"RequestorID":{"@Type":"22","@ID":"PMSConnect"},"BookingChannel":{"@Type":"7","TPA_Extensions":{"BookingWebSource":{"@Code":"","@Url":"https://booking.exely.com/qa/?hotel=501674"}}}}},"UniqueID":{"@Type":"14","@ID":"20260414-501674-1200387942"},"RoomStays":{"RoomStay":[{"@IndexNumber":"0","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001574","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"1"},{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"2"},{"@AgeQualifyingCode":"ChildBandWithoutBed","@Age":"4","@Count":"1","@AgeBucket":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"100"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"},"ServiceRPHs":{"ServiceRPH":[{"@RPH":"2"},{"@RPH":"3"}]}},{"@IndexNumber":"1","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001574","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"160.0000","@AmountAfterTax":"160.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"160.0000","@AmountAfterTax":"160.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"160.0000","@AmountAfterTax":"160.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"160.0000","@AmountAfterTax":"160.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"3"},{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"4"},{"@AgeQualifyingCode":"ChildBandBed","@Age":"4","@Count":"1","@AgeBucket":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"160"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"640.0000","@AmountAfterTax":"640.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"},"ServiceRPHs":{"ServiceRPH":{"@RPH":"4"}}},{"@IndexNumber":"2","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001574","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"100.0000","@AmountAfterTax":"100.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"5"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"100"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"3","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001576","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":[{"@RatePlanID":"10003870"},{"@RatePlanID":"10003541"}]},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"6"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"250"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1000.0000","@AmountAfterTax":"1000.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"4","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001576","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":[{"@RatePlanID":"10003870"},{"@RatePlanID":"10003541"}]},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"7"},{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"8"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"250"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1000.0000","@AmountAfterTax":"1000.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"5","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001576","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"9"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"250"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1000.0000","@AmountAfterTax":"1000.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"6","RoomTypes":{"RoomType":{"@RoomTypeCode":"5001576","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"10"},{"@AgeQualifyingCode":"AdultBed","@Count":"2"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"250"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1000.0000","@AmountAfterTax":"1000.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"7","RoomTypes":{"RoomType":{"@RoomTypeCode":"5003276","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":[{"@RatePlanID":"10003870"},{"@RatePlanID":"10003541"}]},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"11"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"350"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1400.0000","@AmountAfterTax":"1400.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"8","RoomTypes":{"RoomType":{"@RoomTypeCode":"5003276","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":[{"@RatePlanID":"10003870"},{"@RatePlanID":"10003541"}]},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"12"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"},{"@AgeQualifyingCode":"ChildBandBed","@Age":"4","@Count":"1","@AgeBucket":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"400"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1600.0000","@AmountAfterTax":"1600.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"9","RoomTypes":{"RoomType":{"@RoomTypeCode":"5003276","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"350.0000","@AmountAfterTax":"350.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"13"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"350"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1400.0000","@AmountAfterTax":"1400.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}},{"@IndexNumber":"10","RoomTypes":{"RoomType":{"@RoomTypeCode":"5003276","@InvBlockCode":"5000456","@Quantity":"1"}},"RatePlans":{"RatePlan":{"@RatePlanID":"10003870"}},"RoomRates":{"RoomRate":[{"@EffectiveDate":"2026-04-14","@ExpireDate":"2026-04-14","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-15","@ExpireDate":"2026-04-15","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-16","@ExpireDate":"2026-04-16","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}},{"@EffectiveDate":"2026-04-17","@ExpireDate":"2026-04-17","@RatePlanCode":"10003870","Total":{"@AmountBeforeTax":"400.0000","@AmountAfterTax":"400.0000","@CurrencyCode":"USD"}}]},"GuestCounts":{"GuestCount":[{"@AgeQualifyingCode":"AdultBed","@Count":"1","@ResGuestRPH":"14"},{"@AgeQualifyingCode":"AdultBed","@Count":"1"},{"@AgeQualifyingCode":"ChildBandBed","@Age":"4","@Count":"1","@AgeBucket":"1"}]},"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"CancelPenalties":{"@CancelPolicyIndicator":"true","CancelPenalty":{"Deadline":{"@AbsoluteDeadline":"2026-04-13T07:00:00Z"},"AmountPercent":{"@NmbrOfNights":"1","@BasisType":"Nights","@CurrencyCode":"RUB","@Amount":"400"},"PenaltyDescription":{"Text":"In case of cancellation less than 24 hours before 14:00 arrival day you will be charged the cost of the first night"}}},"Total":{"@AmountBeforeTax":"1600.0000","@AmountAfterTax":"1600.0000","@CurrencyCode":"USD","@DecimalPlaces":"0"},"BasicPropertyInfo":{"@HotelCode":"501674"}}]},"ResGuests":{"ResGuest":[{"@ResGuestRPH":"1","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434118","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"GS","MiddleName":"","Surname":"O"},"CitizenCountryName":{"@Code":"KHM"}}}}}},{"@ResGuestRPH":"2","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434119","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"GS","MiddleName":"","Surname":"OO"},"CitizenCountryName":{"@Code":"KHM"}}}}}},{"@ResGuestRPH":"3","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434120","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"GS","MiddleName":"","Surname":"L"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"4","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434121","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"GS","MiddleName":"","Surname":"LL"},"CitizenCountryName":{"@Code":"KHM"}}}}}},{"@ResGuestRPH":"5","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434122","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Gs","MiddleName":"","Surname":"Q"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"6","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434123","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Gs","MiddleName":"","Surname":"Y"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"7","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434124","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Gs","MiddleName":"","Surname":"B"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"8","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434125","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Ges","MiddleName":"","Surname":"Bb"},"CitizenCountryName":{"@Code":"KHM"}}}}}},{"@ResGuestRPH":"9","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434126","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Geuest","MiddleName":"","Surname":"Test"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"10","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434127","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Gest","MiddleName":"","Surname":"Gt"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"11","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434128","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Room","MiddleName":"","Surname":"Sta"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"12","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434129","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Rom","MiddleName":"","Surname":"S"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"13","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434130","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Roommmm","MiddleName":"","Surname":"Ges"},"CitizenCountryName":{"@Code":"GBR"}}}}}},{"@ResGuestRPH":"14","Profiles":{"ProfileInfo":{"UniqueID":{"@Type":"21","@ID":"1200434131","@ID_Context":"PMSConnect"},"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Room","MiddleName":"","Surname":"Gses"},"CitizenCountryName":{"@Code":"GBR"}}}}}}]},"ResGlobalInfo":{"TimeSpan":{"@Start":"2026-04-14T14:00:00","@Duration":"4","@End":"2026-04-18T12:00:00"},"Comments":{"Comment":{"Text":"Guest's comment: Additional information Personal request"}},"Guarantee":{"@GuaranteeCode":"None","Comments":{"Comment":[{"@Name":"PaymentMethodName","Text":"PayOnArrival"},{"@Name":"PaymentSystemName","Text":"AT_ARRIVAL"},{"@Name":"PaymentSystemCode","Text":"5003924"},{"@Name":"PaymentSystemTitle","Text":"At check-in"}]}},"Total":{"@AmountBeforeTax":"11739.0000","@AmountAfterTax":"11739.0000","@CurrencyCode":"USD"},"Profiles":{"ProfileInfo":{"Profile":{"Customer":{"@Gender":"Unknown","PersonName":{"GivenName":"Heng","MiddleName":"","Surname":"Guest"},"Telephone":{"@PhoneNumber":"+855715194987"},"Email":"lakleabheng@gmail.com"}}}}},"Services":{"Service":[{"@ServicePricingType":"Per stay","@ServiceRPH":"1","@Inclusive":"false","@Quantity":"1","@ID":"5002979","ServiceDetails":{"TimeSpan":{"@Start":"2026-04-14T00:00:00","@Duration":"1"},"Comments":{"Comment":{"@Name":"Test Service","Text":"test services desition"}},"Total":{"@AmountBeforeTax":"250.0000","@AmountAfterTax":"250.0000","@CurrencyCode":"USD"}}},{"@ServicePricingType":"Per stay","@ServiceRPH":"2","@Inclusive":"false","@Quantity":"1","@ID":"5002999","ServiceDetails":{"TimeSpan":{"@Start":"2026-04-14T00:00:00","@Duration":"1"},"Comments":{"Comment":{"@Name":"Test Test","Text":"Test Test"}},"Total":{"@AmountBeforeTax":"1.0000","@AmountAfterTax":"1.0000","@CurrencyCode":"USD"}}},{"@ServicePricingType":"Per person per night","@ServiceRPH":"3","@Inclusive":"false","@Quantity":"3","@ID":"5002998","ServiceDetails":{"TimeSpan":{"@Start":"2026-04-14T00:00:00","@Duration":"4"},"Comments":{"Comment":{"@Name":"American breakfast","Text":"American breakfast test"}},"Total":{"@AmountBeforeTax":"24.0000","@AmountAfterTax":"24.0000","@CurrencyCode":"USD"},"ServiceRates":{"ServiceRate":[{"@EffectiveDate":"2026-04-14","@AmountAfterTax":"6.0000"},{"@EffectiveDate":"2026-04-15","@AmountAfterTax":"6.0000"},{"@EffectiveDate":"2026-04-16","@AmountAfterTax":"6.0000"},{"@EffectiveDate":"2026-04-17","@AmountAfterTax":"6.0000"}]}}},{"@ServicePricingType":"Per person per night","@ServiceRPH":"4","@Inclusive":"false","@Quantity":"3","@ID":"5002998","ServiceDetails":{"TimeSpan":{"@Start":"2026-04-14T00:00:00","@Duration":"4"},"Comments":{"Comment":{"@Name":"American breakfast","Text":"American breakfast test"}},"Total":{"@AmountBeforeTax":"24.0000","@AmountAfterTax":"24.0000","@CurrencyCode":"USD"},"ServiceRates":{"ServiceRate":[{"@EffectiveDate":"2026-04-14","@AmountAfterTax":"6.0000"},{"@EffectiveDate":"2026-04-15","@AmountAfterTax":"6.0000"},{"@EffectiveDate":"2026-04-16","@AmountAfterTax":"6.0000"},{"@EffectiveDate":"2026-04-17","@AmountAfterTax":"6.0000"}]}}}]}}},"Success":""}}}}}
    data = map_exely_to_reservation(booking,property)
    booking_confirmation = []
    if data:
        for d in data:
            try:
                edoor_data = add_new_reservation(
                    d.get("doc"),
                    sync_room_available_to_channel_manager=False
                )
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
        if booking_confirmation:
            return confirmation_message_booking(booking_confirmation, property)
        # frappe.enqueue(
        #         "edoor.channel_managers.exely.availability.update_room_availability",
        #         queue="channel_manager",
        #         property="ESTC HOTEL 6"
        #     )
        
    else:
        frappe.log_error("No new bookings to add from Exely", "Exely Booking Sync")