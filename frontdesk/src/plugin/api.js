
import {inject, reactive} from 'vue'
import {toaster} from './toast'
import {handleServerMessage} from './handle-server-message'
import { FrappeApp } from 'frappe-js-sdk';
export function getDoc(doctype, name){
    const frappe = new FrappeApp()
    const db = frappe.db()
    return  new Promise((resolve, reject)=>{
        db.getDoc(doctype, name)
        .then((doc) => { 
            resolve(doc)
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(message)
        });
    })
}
export function getDocList(doctype, option){
    const frappe = new FrappeApp()
    const db = frappe.db()
    return new Promise((resolve, reject)=>{
        db.getDocList(doctype, option)
        .then((doc) => {
            resolve(doc)
        })
        .catch((error) => {
            reject(error)
            toaster('error', 'Server Error');
        });
    })
}
export function updateDoc(doctype, name, data, message){
    const frappe = new FrappeApp()
    const db = frappe.db()
    return new Promise((resolve, reject)=>{
        db.updateDoc(doctype, name, data)
        .then((doc) => {
            resolve(doc)
            toaster('success', `${message ? message : 'Update successful'}`)
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(message)
            toaster('error', 'Server Error');
        });
    })
}
export function getApi(api, params = Object){
    const frappe = new FrappeApp()
    const call = frappe.call()
    return new Promise((resolve, reject)=>{
        call.get(`edoor.api.${api}`, params).then((result) => {
            resolve(result)
        }).catch((error) =>{
            handleServerMessage(error)
            reject(error)
        })
    })
}

export function uploadFiles(files, fileArgs = Object){
    const frappe = new FrappeApp()
    const file = frappe.file();
    console.log(fileArgs)
    return new Promise((resolve, reject)=>{
        let countFile = 0
        files.forEach((r)=>{
            file.uploadFile(
                r,
                fileArgs
            )
            .then((r) => {
                if(r.data && r.data.message){
                    countFile++
                    if(countFile == files.length){
                        toaster('success', 'Upload files successfull.')
                        resolve(true)
                    }
                }
                
            })
            .catch((error) =>{
                handleServerMessage(error)
                reject(error)
            })
        })
    })
    
}