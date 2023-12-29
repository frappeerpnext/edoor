<template>
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading">
    
    <div class="grid">
        <div class="col-6">
            <label>Posting Date</label>
            <div>
                <Calendar showButtonBar panelClass="no-btn-clear" selectOtherMonths class="w-full" showIcon v-model="data.posting_date"  :min-date="working_day" dateFormat="dd-mm-yy"/>
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
            <ComAutoComplete v-model="data.guest" :suggestions="data.selected_customer" placeholder="Select Guest" doctype="Customer"
            :isAddNew="true"
            @onAddNew="onAddNewGuest"
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
import { ref, inject, onMounted, getApi, getDoc, createUpdateDoc,useDialog } from '@/plugin'
import ComAddGuest from "@/views/guest/components/ComAddGuest.vue"
const dialogRef = inject('dialogRef')
const loading=ref(false)
const data =ref({})
const working_day = moment(window.current_working_date).toDate()
const property = JSON.parse(localStorage.getItem("edoor_property"))
const gv = inject('$gv');
const dialog = useDialog()
 

function onAddNewGuest(name){
    dialog.open(ComAddGuest, {
        data:{
            guest_name: name
        },
        props: {
            header: `Add New Guest`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose:(options) => {
            const result = options.data;

            if(result){
                
                data.value.selected_customer = [ { "value": result.name, "description": result.name + "-" + result.customer_name_en, "label": result.name } ]
                data.value.guest = result.name
			}
        }
    });  
}

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
    createUpdateDoc('Deposit Ledger', savedData).then((r)=>{
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
    if(dialogRef.value.data.name){
        getDoc("Deposit Ledger", dialogRef.value.data.name).then(d=>{
            data.value = d
            data.value.posting_date = moment(d.posting_date).toDate()
        })

    }else {
        data.value.posting_date = moment(window.current_working_date).toDate()
    }
    

 
})
</script>