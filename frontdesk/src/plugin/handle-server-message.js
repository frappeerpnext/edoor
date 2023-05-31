
import {inject, reactive} from 'vue'
import {toaster} from './toast'

export function getDoc(doctype, name){
    const frappe = inject('$frappe')
    const db = frappe.db()
    return  new Promise((resolve, reject)=>{
        db.getDoc(doctype, name)
        .then((doc) => {
            console.log(doc)
            resolve(doc)
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(message)
        });
    })
}

export function handleServerMessage(m){
    console.log(m)
    toaster.error(JSON.stringify(m))
 
    const dictionary = [
        {exception: 'frappe.exceptions.MandatoryError', text: 'Invalid input'}
    ]
    const message = JSON.parse(JSON.stringify(m))
    if(message.httpStatus == 417){
        var arrException = []
        if(message.exception){
            arrException = message.exception.split(':')
            console.log(arrException)
            if(arrException[0]){
                if(arrException[0] == 'frappe.exceptions.ValidationError')
                    return arrException[1]
                const msg = dictionary.find((r)=>r.exception == arrException[0])
                return msg.text
            }
        }
    }else{

        return message.httpStatusText
    }
}

export function showToast(){
    toaster('success','xxxx')
}