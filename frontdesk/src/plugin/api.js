
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
            window.postMessage('show_error|' + 'Server Error', '*')
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
            window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(error) 
        });
    })
}
export function createUpdateDoc(doctype, data, message){
    const frappe = new FrappeApp()
    const db = frappe.db()
    return new Promise((resolve, reject)=>{
        if(data.name){
            db.updateDoc(doctype, data.name, data)
            .then((doc) => {
                resolve(doc) 
                window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
            })
            .catch((error) => {
                const message = handleServerMessage(error)
                reject(error) 
            });
        }
        else{
            db.createDoc(doctype, data)
            .then((doc) => {
                resolve(doc)
                window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
                
            })
            .catch((error) => {
                const message = handleServerMessage(error)
                reject(error) 
            });
        }
    })
}
export function deleteDoc(doctype, name, message){
    const frappe = new FrappeApp()
    const db = frappe.db()
    return new Promise((resolve, reject)=>{
        db.deleteDoc(doctype, name)
        .then((doc) => {
            resolve(doc.message)
            window.postMessage('show_success|' + `${message ? message : 'Deleted successful'}`, '*')
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(message) 
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
export function postApi(api, params = Object, message){
    const frappe = new FrappeApp()
    const call = frappe.call()
    return new Promise((resolve, reject)=>{
        call.post(`edoor.api.${api}`, params).then((result) => {
            window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
            resolve(result)
        }).catch((error) =>{
            handleServerMessage(error)
            reject(error)
        })
    })
}
export function deleteApi(api, params = Object, message){
    const frappe = new FrappeApp()
    const call = frappe.call()
    return new Promise((resolve, reject)=>{
        call.delete(`edoor.api.${api}`, params).then((result) => {
            window.postMessage('show_success|' + `${message ? message : 'Deleted successful'}`, '*')
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
                        window.postMessage('show_success|' + 'Upload files successfull.', '*')
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

