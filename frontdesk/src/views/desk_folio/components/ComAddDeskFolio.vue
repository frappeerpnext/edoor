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
            <label for="room">Guest<span class="text-red-500">*</span></label>
            <ComAutoComplete v-model="data.guest" placeholder="Select Guest" doctype="Customer"
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
import { ref, inject, onMounted, getApi, getDoc, createUpdateDoc } from '@/plugin'

const dialogRef = inject('dialogRef')
const loading=ref(false)
const data =ref({})
const working_day = moment(window.current_working_date).toDate()
const property = JSON.parse(localStorage.getItem("edoor_property"))
const gv = inject('$gv');

function onOK() {
    loading.value = true
    var savedData = {
        name: data.value.name,
        posting_date: gv.dateApiFormat(data.value.posting_date),
        room_id: data.value.room_id,
        note: data.value.note,
        property: property.name,
        guest:data.value.guest
    }
    createUpdateDoc('Desk Folio', {data: savedData}).then((r)=>{
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
    // data.value.naming_series='FN.YYYY.-.####'; 
    data.value.posting_date = moment(window.current_working_date).toDate()
    data.value.working_day = moment(window.current_working_date).toDate()
})
</script>