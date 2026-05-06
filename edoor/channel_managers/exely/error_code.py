# priority lower number is priority

EXELY_ERROR_CODES = {
    "15": {
        "message": "Invalid date",
    },
    "61": {
        "message": "Invalid currency code",
        "action": "Stop Sync",
        "priority":1
    },
    "69": {
        "message": "Minimum stay criteria not fulfilled",
        "type": "3"
    },
    "87": {
        "message": "Booking reference invalid",
        "type": None
    },
    "94": {
        "message": "Same booking references",
        "type": None
    },
    "97": {
        "message": "Booking reference not found",
        "type": None
    },
    "135": {
        "message": "End date invalid",
        "type": None
    },
    "136": {
        "message": "Start date invalid",
        "type": None
    },
    "150": {
        "message": "Changes are not permitted",
        "type": None,
        "action":"Stop Sync",
        "priority":1
    },
    "163": {
        "message": "Payment type invalid",
        "type": None,
        "action": "Stop Sync",
        "priority":1
    },
    "175": {
        "message": "Password invalid",
        "type": "4",
        "action": "Stop Sync",
        "priority":1
    },
    "182": {
        "message": "Password required",
        "type": "4",
        "action": "Stop Sync",
        "priority":1
    },
    "187": {
        "message": "System currently unavailable",
        "type": "12",
        "action": "Delay Sync",
        "delay": 60*5,
        "priority":2
    },
    "188": {
        "message": "Transaction error - please report",
        "type": "13"
    },
    "240": {
        "message": "Bank card expired",
        "type": None
    },
    "241": {
        "message": "Expiry date is invalid",
        "type": None
    },
    "242": {
        "message": "Bank card number is invalid or missing",
        "type": None
    },
    "281": {
        "message": "Reservation requires bank card data",
        "type": "10"
    },
    "320": {
        "message": "Invalid value",
        "type": "3",
        "action": "Delay Sync",
        "delay":60*5,
        "priority":2
    },
    "321": {
        "message": "Required field missing",
        "type": "10"
    },
    "322": {
        "message": "No availability",
        "type": "3"
    },
    "361": {
        "message": "Invalid hotel",
        "type": None
    },
    "365": {
        "message": "Bank card error",
        "type": "13"
    },
    "375": {
        "message": "Hotel not active",
        "type": None
    },
    "392": {
        "message": "Invalid hotel code",
        "type": None
    },
    "400": {
        "message": "Invalid property code",
        "type": None
    },
    "402": {
        "message": "Invalid room type",
        "type": None
    },
    "425": {
        "message": "No match found",
        "type": None
    },
    "433": {
        "message": "Please book on a separate reservation",
        "type": None
    },
    "436": {
        "message": "Rate plan does not exist",
        "type": None
    },
    "437": {
        "message": "Rate plan unavailable",
        "type": None
    },
    "438": {
        "message": "Requested rate plan not available",
        "type": None
    },
    "448": {
        "message": "System error",
        "type": "13"
    },
    "450": {
        "message": "Unable to process",
        "type": "13",
        "action":"Stop Sync",
        "priority":1
    },
    "504": {
        "message": "Extra bed or crib not available",
        "type": None
    },
    "505": {
        "message": "Invalid bed type",
        "action":"Stop Sync",
        "priority":1
    },
    "730": {
        "message": "Invalid room type for requested hotel",
        "type": None,
        "action":"Stop Sync",
        "priority":1
    },
    "767": {
        "message": "Invalid room stay index",
        "type": None
    },
    "769": {
        "message": "Only first reservation processed",
        "type": None
    },
    "783": {
        "message": "Room or rate plan not found",
        "type": None,
        "action":"Stop Sync",
        "priority":1
    },
    "784": {
        "message": "Request timed out. Please retry",
        "type": None,
        "action":"Delay Sync",
        "priority":2,
        "delay":60*5,
    },
    "840": {
        "message": "Duplicated rate plan codes",
        "type": None,
    },
    "852": {
        "message": "Invalid children ages",
        "action":"Stop Sync",
        "priority":1,
    }
}