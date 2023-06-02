import {toaster} from './toast'
export function handleServerMessage(m){
    console.log(m) 
    const dictionary = [
        {exception: 'frappe.exceptions.MandatoryError', text: 'Invalid input'},
        {exception: 'frappe.exceptions.TimestampMismatchError', text: 'Please refresh to get the latest document.'}
    ]
    const message = JSON.parse(JSON.stringify(m))
    if(message.httpStatus == 417){
        var arrException = []
        if(message.exception){
            if(Array.isArray(message.exception)){
                arrException = message.exception
            }
            else if(message.exception){
                arrException = message.exception.split(':')
                console.log(arrException)
            }
            if(arrException[0]){
                if(arrException[0] == 'frappe.exceptions.ValidationError')
                    toaster('warn',arrException[1])
                else{
                    const msg = dictionary.find((r)=>r.exception == arrException[0])
                    if(msg.text)
                        toaster('warn',msg.text)
                }
                    
            }
        }
    }else{
        toaster('error',message.httpStatusText)
    }
}