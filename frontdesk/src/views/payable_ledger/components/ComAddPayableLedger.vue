<template>
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading">
    <div class="grid">

        <div class="col-6">
            <label>Posting Date</label>
            <div>
                <Calendar selectOtherMonths class="w-full" showIcon v-model="data.posting_date" :manualInput="false" :disabled="true" :min-date="working_day" dateFormat="dd-mm-yy"/>
            </div>
        </div> 
        <div class="col-6">
            <label> Room</label>
            <div class="w-full">
                <ComAutoComplete placeholder="Select Room"  v-model="data.room_id" class="pb-2 w-full"  doctype="Room" :filters="['property','=',property.name]" :disabled="doc?.docstatus==1" />
            </div>
        </div>
        
        <div class="col-12">
            <label for="room">Vendor<span class="text-red-500">*</span></label>
            <ComAutoComplete v-model="data.vendor" placeholder="Select Vendor" doctype="Vendor"
                class="auto__Com_Cus w-full"/>
        </div>
        <div class="col-12">
        <label>Note</label>
        <div class=" card w-full flex justify-content-left">
            <Textarea class="w-full" v-model="data.note" autoResize />
        </div>
    </div> 
    </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted, getDoc, createUpdateDoc,useToast } from '@/plugin'

const dialogRef = inject('dialogRef')
const loading=ref(false)
const data =ref({})
const working_day = moment(window.current_working_date).toDate()
const property = JSON.parse(localStorage.getItem("edoor_property"))
const gv = inject('$gv');
const toast = useToast();
function onOK() {
    if(!data.value.vendor){
        toast.add({ severity: 'warn', summary: "Add Payable Ledger", detail: "Please select vendor for add payable ledger.", life: 5000 })
        return
    }
    
    loading.value = true
    var savedData = {
        name: data.value.name,
        posting_date: gv.dateApiFormat(data.value.posting_date),
        working_day:working_day,
        room_id: data.value.room_id,
        note: data.value.note,
        property: property.name,
        vendor:data?.value.vendor
    }
    createUpdateDoc('Payable Ledger', savedData).then((r)=>{
        dialogRef.value.close(r)
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
}
function onClose(param = false) {
    dialogRef.value.close(param)
}
onMounted(()=> {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    // data.value.naming_series='FN.YYYY.-.####'; 
    if(dialogRef.value.data.name){
        getDoc("Payable Ledger", dialogRef.value.data.name).then(d=>{
            data.value = d
            data.value.posting_date = moment(d.posting_date).toDate()
        })

    }else {
        data.value.posting_date = moment(window.current_working_date).toDate()
    }
})
</script>