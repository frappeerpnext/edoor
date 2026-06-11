import socket
import frappe
from edoor.integration.door_lock.log import create_log,add_issue_card
from edoor.integration.door_lock.utils import get_door_lock_setting

from frappe.utils import get_datetime

def get_setting(property):
    setting = get_door_lock_setting(property)
    if not setting.get("ip") or not setting.get("port"):
        frappe.throw("Please setup door access log setting in property setting.") 
    
    # # test connection
    # resp = test_connection(setting.get("ip"), int(setting.get("port") or 10086))
    
    # if resp.get("success") == False:
    #     frappe.throw(
    #         "Unable to connect to the key card reader device. Please ensure the device is connected, the door lock app server is running, and the door lock integration is configured correctly."
    #     )

    return setting

def send_command(command, setting):
    """
    Send command to card encoder via TCP.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    response = None 

    try:
        sock.connect((setting.get("ip"), int(setting.get("port") or 0)))

        frappe.logger().info(f"Card Encoder Command: {command}")

        sock.sendall(command.encode("ascii"))

        res = sock.recv(4096).decode("ascii")
        
        response =  res

    except socket.timeout:
        response = {"success":False, "message":"ERROR: Device did not respond within 10 seconds"} 
    except Exception as e:
        
        response = {"success":False, "message":f"ERROR: {str(e)}"}

    finally:
        sock.close()

 
    return response



def parse_response(response):
    """
    Convert:
    KA|AS00|MSCardEraseOK

    Into:
    {
        "AS": "00",
        "MS": "CardEraseOK"
    }
    """
    
    if  isinstance(response, dict):
        frappe.throw(
            "Unable to connect to the key card reader device. Please ensure the device is connected, the door lock app server is running, and the door lock integration is configured correctly."
        )

    result = {
        "raw_response": response
    }

    for part in response.split("|"):
        if len(part) >= 2:
            result[part[:2]] = part[2:]

    return result


@frappe.whitelist()
def test_connection(IP,PORT):
    """
    Test TCP connection to encoder.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((IP, PORT))
     
        return {
            "success": True,
            "message": "Connected successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Card Encoder Connection Error")

        return {
            "success": False,
            "message": str(e)
        }

    finally:
        sock.close()


@frappe.whitelist(methods=["POST"])
def write_guest_card(
    property,
    stay_data
):
    setting = get_setting(property)
    # check card_info
    card_info = read_card(property)
    
    if card_info.get("card_type"):
        if not card_info.get("card_type") in ["Guest Card","Check-Out Card","UNKNOWN"]:
            frappe.throw("You cannot write check in card on a {0}".format(card_info.get("card_type")))

 

    # guest card
    if not stay_data or not stay_data.get("reservation_stay"):
        frappe.throw("Please select reservation for guest card")
    if not stay_data.get("room_id"):
        frappe.throw("Please select room number for guest card")
    
    room_doc  = frappe.get_cached_doc("Room",stay_data.get("room_id"))
    

    if not room_doc.door_lock_no:
        frappe.throw("Rooom number {0} has no mapping with door access lock number. Please update door lock number in room management.".format(room_doc.room_number))
    


    stay_doc  = frappe.get_doc("Reservation Stay",stay_data.get("reservation_stay") ) 


  
    departure_time = stay_data.get("departure_time") or  stay_doc.departure_time      # e.g. "9:55:56.301794"
    
    dt = get_datetime(departure_time)

    checked_out_time = dt.strftime("%y%m%d%H%M")
    reservation_departure_time =  dt.strftime("%H:%M:%S.%f")


    # 9:55:56.301794
   

    building_no = room_doc.building_no or "01"

    doc ={
        "reservation_stay": stay_doc.name,
        "room":room_doc.name,
        "building": building_no,
        "lock_no": room_doc.door_lock_no,
        "card_type":"06",
        "note":stay_data.get("note"),
        "expire": dt,
        "property":property,
        "guest": stay_doc.guest
    }
    log = create_log(data=doc)


    command = (
        f"KR"
        f"|BN{building_no}"
        f"|CN9999"
        f"|RN{room_doc.door_lock_no}"
        f"|CT06"
        f"|CO{checked_out_time}"
        f"|LS00"
    )
 
 
    
    resp = write_card(command = command, setting =setting)


    log.card_id = resp.get("id")
    log.status = "Success" if resp.get("success") else "Fail"
    log.fail_note  = ""  if resp.get("success") else resp.get("message")
    log.save()
    if log.status =="Success":
        if log.reservation_stay:
            
            frappe.db.sql(
                "update `tabReservation Stay` set departure_time = %(departure_time)s where name =%(reservation_stay)s",
                {"departure_time":reservation_departure_time,"reservation_stay":log.reservation_stay}
            )

    # check if card info if have in card issue list then release it
    if card_info.get("ID"):

        frappe.db.sql("update `tabDoor Lock Issue Card` set status = 'Release' where card_id = %(card_id)s and property=%(property)s",{
            "property":property,
            "card_id":card_info.get("ID")
        } )

        # create issue card record
        issue_card_data = {
            "property":property,
            "reservation_stay":log.reservation_stay,
            "room":log.room,
            "card_id":log.card_id,
            "card_type":"06",
            "expire":log.expire,
            "posting_date":frappe.utils.nowdate()
        }
        add_issue_card(issue_card_data)
    frappe.db.commit()

    if resp.get("success"):
        frappe.msgprint("Write guest card successfully")
    else:
        
        frappe.throw(
            "Unable to write to the guest card. Please make sure the card is placed correctly on the card reader and try again."
        )

    return  resp

@frappe.whitelist(methods=["POST"])
def write_check_out_card(
    property,
    stay_data
):
    setting = get_setting(property)
    card_info = read_card(property)
    
    if card_info.get("card_type"):
        if not card_info.get("card_type") in ["Guest Card","Check-Out Card","UNKNOWN"]:
            frappe.throw("This card is not a guest card or blank card")

    
    # guest card
    if not stay_data or not stay_data.get("reservation_stay"):
        frappe.throw("Please select reservation for check out guest card")
    if not stay_data.get("room_id"):
        frappe.throw("You cannot write check out card on a {0}".format(card_info.get("card_type")))
    
    room_doc  = frappe.get_cached_doc("Room",stay_data.get("room_id"))
    

    if not room_doc.door_lock_no:
        frappe.throw("Rooom number {0} has no mapping with door access lock number. Please update door lock number in room management.".format(room_doc.room_number))
    


    stay_doc  = frappe.get_doc("Reservation Stay",stay_data.get("reservation_stay") ) 
    if stay_doc.reservation_status  != "Checked Out":
        frappe.throw("This room {0} is not a check out room".format(room_doc.room_number))


  
    departure_time = f"{stay_doc.departure_date} {stay_doc.departure_time}"       
    
    
    dt = get_datetime(departure_time)

    checked_out_time = dt.strftime("%y%m%d%H%M")
   

    building_no = room_doc.building_no or "01"

    doc ={
        "reservation_stay": stay_doc.name,
        "room":room_doc.name,
        "building": building_no,
        "lock_no": room_doc.door_lock_no,
        "card_type":"07",
        "note":stay_data.get("note"),
        "expire": dt,
        "property":property,
        "guest": stay_doc.guest
    }
    log = create_log(data=doc)


    command = (
        f"KR"
        f"|BN{building_no}"
        f"|CN{stay_doc.name}"
        f"|RN{room_doc.door_lock_no}"
        f"|CT07"
        f"|CO{checked_out_time}"
        f"|LS00"
    )
 
    
    resp = write_card(command = command, setting =setting)
    log.card_id = resp.get("id")
    log.status = "Success" if resp.get("success") else "Fail";
    log.fail_note  = ""  if resp.get("success") else resp.get("message")
    log.save()

    #check card info if have card id update issue card
    if card_info.get("ID"):
        frappe.db.sql("update `tabDoor Lock Issue Card` set status = 'Release' where card_id = %(card_id)s and property=%(property)s",{
            "property":property,
            "card_id":card_info.get("ID")
        } )
        

    
    frappe.db.commit()

    if resp.get("success"):
        frappe.msgprint("Write check out guest card successfully")
    else:
        
        frappe.throw(
            "Unable to write to the guest card. Please make sure the card is placed correctly on the card reader and try again."
        )

    return  resp

 


@frappe.whitelist(methods=["POST"])
def write_employee_card(
    property,
    data
):
    if not data.get("employee"):
        frappe.thow("Please select employee for issue staff card")

    setting = get_setting(property)
    # check card_info
    card_info = read_card(property)
    

    # guest card
    card_type = data.get("card_type")
    
    if card_type=="08"  and not data.get("area"):
        frappe.throw("Please select area for area card")
    
    if card_type=="C"  and not data.get("building"):
        frappe.throw("Please select building for buiding card")
    
    
    if card_type=="D"  and not data.get("floor"):
        frappe.throw("Please select floor for floor card")
        
    
    
    expire_date_time = data.get("expire")
    dt = get_datetime(expire_date_time)
    expire_date_time = dt.strftime("%y%m%d%H%M")
    



    # 9:55:56.301794
   

    

    doc ={
        "building": data.get("building") or "",
        "area": data.get("area") or "",
        "floor": data.get("floor") or "",
        "card_type":data.get("card_type"),
        "note":data.get("note"),
        "expire": dt,
        "property":property,
        "employee":data.get("employee")
    }
    log = create_log(data=doc)

    command = None
    if card_type in ["A","B"]:
        command = (
            f"KR"
            f"|RN01010D"
            f"|CT{card_type}"
            f"|CO{expire_date_time}"
            f"|LS00"
        )
    elif card_type =="8" or card_type=="08":
        area = data.get("area") or 1
        area =  f"{area:02d}"
        command = (
            f"KR"
            f"|CT08"
            f"|AN{area}"
            f"|CO{expire_date_time}"
            f"|LS00"
        )
    elif card_type =="C":
        area = data.get("area") or 1
        area =  f"{area:02d}"
        
        buiding = data.get("building") or 1
        buiding =  f"{buiding:02d}"

        command = (
            f"KR"
            f"|CTC"
            f"|AN{area}"
            f"|BN{buiding}"
            f"|CO{expire_date_time}"
            f"|LS00"
        )
    elif card_type =="D":
        area = data.get("area") or 1
        area =  f"{area:02d}"
        
        building = data.get("building") or 1
        building =  f"{building:02d}"
        
        floor = data.get("floor") or 1
        floor =  f"{floor:02d}"


        command = (
            f"KR"
            f"|CTC"
            f"|AN{area}"
            f"|BN{building}"
            f"|FN{floor}"
            f"|CO{expire_date_time}"
            f"|LS00"
        )

 
 
    
    resp = write_card(command = command, setting =setting)


    log.card_id = resp.get("id")
    log.status = "Success" if resp.get("success") else "Fail"
    log.fail_note  = ""  if resp.get("success") else resp.get("message")
    log.save()
    
    # check if card info if have in card issue list then release it
    if card_info.get("ID"):
        frappe.db.sql("update `tabDoor Lock Issue Card` set status = 'Release' where card_id = %(card_id)s and property=%(property)s",{
            "property":property,
            "card_id":card_info.get("ID")
        } )

        # create issue card record
        issue_card_data = {
            "property":property,
            "employee":data.get("employee"),
            "building":data.get("building") or "01",
            "area":data.get("area") or "01",
            "floor":data.get("floor") or "01",
            "card_id":log.card_id,
            "card_type":card_type,
            "expire":log.expire,
            "posting_date":frappe.utils.nowdate()
        }
        add_issue_card(issue_card_data)
    frappe.db.commit()

    if resp.get("success"):
        frappe.msgprint("Issue {0} card successfully".format(data.get("card_type_name")))
    else:
        
        frappe.throw(
            "Unable to write to the {0} card. Please make sure the card is placed correctly on the card reader and try again.".format(data.get("card_type_name"))
        )

    return  resp



@frappe.whitelist(methods=["POST"])
def write_card(
    building_no="01",
    card_no="01010101",
    room_no="1-2013",
    lock_no="01010D",
    card_type="06",
    expire="2606031400",
    loss_flag="00", 
    command = None,
    setting=None

):
    """
    Write room card.
    """

    command =   command or (
        f"KR"
        f"|BN{building_no}"
        f"|CN{card_no}"
        f"|RN{lock_no}"
        f"|CT{card_type}"
        f"|CO{expire}"
        f"|LS{loss_flag}"
    )
 

    response = send_command(command,setting)
    
    
    status = "Success"
    if  isinstance(response, dict):
        status = response.get("success")
    card_id = ""
    if   isinstance(response, str):
        resp =  parse_response(response)
        
        card_id = resp.get("ID") or ""
    
    
    
    return {
        "success":status,
        "id":  card_id,
        "message":  parse_response(response) if  status=="Success" and isinstance(response, str) else response.get("message")
    }




@frappe.whitelist(  )
def read_card(property):
    
    setting = get_setting(property)

    response = send_command("KI", setting)
    
    data =  parse_response(response)
    response_data = {}
    
    if data.get("CT") in ["Guest Card","Check-Out Card"]:
        
        response_data =  get_reservation_data(data.get("ID"))

    response_data["card_type"] = data.get("CT")
    response_data["ID"] = data.get("ID")
    return response_data


def get_reservation_data(card_id):
    
    sql="select * from `tabDoor Lock Log` where card_id=%(card_id)s order by creation desc limit 1"
    data = frappe.db.sql(sql,{"card_id":card_id},as_dict = 1)
    
    if data:
        data = data[0]
    else:
        data= {}

    if data.get("reservation_stay"):
        doc = frappe.get_cached_doc("Reservation Stay", data.get("reservation_stay"))
        return {
            "reservation_stay": doc.name,
            "arrival_date":doc.arrival_date,
            "departure_date":doc.departure_date,
            "departure_time": f"{doc.departure_date} {doc.departure_time}",
            "guest":doc.guest,
            "guest_name":doc.guest_name,
            "note": data.get("note"),
            "room_id":data.get("room"),
            "room_number":frappe.get_cached_value("Room",data.get("room"),"room_number"),
            "business_source": doc.business_source
        }
    return {}
     
@frappe.whitelist()
def erase_card(property=None,note=None):
    """
    Erase / reset card.
    """
    setting = get_setting(property)

    card_info = read_card(property)    
    if card_info.get("card_type"):
        if not card_info.get("card_type") in ["Guest Card","Check-Out Card","UNKNOWN"]:
            frappe.throw("You cannot erase {0}".format(card_info.get("card_type")))


    doc ={
        "card_type":"00",
        "property":property
    }
    

    if card_info.get("card_type") in ["Guest Card","Check-Out Card"]: 
        room_doc = frappe.get_cached_doc("Room",card_info.get("room_id"))
        doc ={
            "reservation_stay": card_info.get("reservation_stay"),
            "room":card_info.get("room_id"),
            "building": room_doc.building_no,
            "lock_no": room_doc.door_lock_no,
            "card_type":"00",
            "note":note or "",
            "property":property,
            "guest": card_info.get("guest")
        }
    
    
    log = create_log(data=doc)



    
    response = send_command("KD",setting)
    if  isinstance(response, dict):
        log.status = "Success"
        log.save()
        frappe.db.commit()
    else:
        log.status = "Fail"
        log.save()
        frappe.db.commit()


    
    if log.status == "Success":
        frappe.msgprint("Reset card successfully")
    else:
        
        frappe.throw(
            "Unable to write to the guest card. Please make sure the card is placed correctly on the card reader and try again."
        )


    return   "Done"


def format_device_datetime(value):
    """
    2606031400 -> 2026-06-03 14:00
    """
    if len(value) != 10:
        return value

    return (
        f"20{value[0:2]}-"
        f"{value[2:4]}-"
        f"{value[4:6]} "
        f"{value[6:8]}:"
        f"{value[8:10]}"
    )

