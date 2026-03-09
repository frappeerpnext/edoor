// import { createPromiseDialog } from "vue-promise-dialogs"


interface params {
    doctype?:String,
    name?:String,
    text?: String,
    title?: String,
    type?: String,
    report?:String, 
    value?:String,
    print:{
            type:Boolean,
            default:0
        },
    data:Object,//use in comSelectSaleOrder
    table:Object, //use in comSelectSaleOrder
    permissionCode:String
}
// export  const viewHappyHourPromotionModal = createPromiseDialog<params, object>(ComViewHappyHourPromotionModal);

