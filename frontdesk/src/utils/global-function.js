

import {getDocument,createDocument,getData,getDocumentList ,postData } from "@/plugin/api.js";
import * as reservation from "@/utils/global/reservation.js";
import * as utils from "@/utils/utils.js";
 
globalThis.app = globalThis.app || {};
globalThis.app.utils = utils


// api url 
globalThis.app.getDoc =  async function (DocType,DocName) {
  return await getDocument(DocType,DocName)
}

globalThis.app.createDoc =  async function (DocType,params) {
  return await createDocument(DocType,params)
}

globalThis.app.updateDoc =  async function (DocType,name,params) {
  return await updateDocument(DocType,name,params)
}

 
globalThis.app.getApi =  async function (api_url,param) {
  return await getData(api_url,param)
}

 
globalThis.app.postApi =  async function (api_url,param,message="",show_message=true) {
  return await postData(api_url,param,message,show_message)
}

globalThis.app.getDocList =  async function (DocType,param) {
  return await getDocumentList(DocType,param)
}


// reservatrion 
globalThis.app.viewReservationDetail =  async function (name) {
  return await reservation.viewReservationDetail(name)
}

//Group Assign Room
globalThis.app.openGroupAssignRoom =  async function (name) {
  return await reservation.onOpenGroupAssignRoom(name)
}


// toast servce
globalThis.app.showWarning =  async function (title, message = "") {
  utils.showWarning(title,message)
}
