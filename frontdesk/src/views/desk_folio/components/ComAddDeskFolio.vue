<template>
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading">
    <div class="grid">

        <div class="col-6">
            <label>{{$t('Posting Date')}}</label>
            <div>
                <Calendar selectOtherMonths class="w-full" showIcon v-model="data.posting_date" :manualInput="false" :disabled="false" :max-date="working_day" dateFormat="dd-mm-yy"/>
            </div>
        </div> 
        <div class="col-6">
            <label>{{ $t('Room') }} </label>
            <div class="w-full">
                <ComAutoComplete placeholder="Select Room"  v-model="data.room_id" class="pb-2 w-full"  doctype="Room" :filters="['property','=',property.name]" :disabled="doc?.docstatus==1" />
            </div>
        </div>
        
        <div class="col-12">
            <label for="room">{{$t('Guest')}}<span class="text-red-500">*</span></label>
            <ComAutoComplete v-model="data.guest" placeholder="Select Guest" doctype="Customer" :isAddNew="true" @onAddNew="onAddNewGuest"
                class="auto__Com_Cus w-full"/>
        </div>
        <div class="col-12">
        <label>{{ $t('Note') }} </label>
        <div class=" card w-full flex justify-content-left">
            <Textarea class="w-full" v-model="data.note" autoResize />
        </div>
    </div> 
    </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted, getDoc, createUpdateDoc,useToast,useDialog } from '@/plugin'
import ComAddGuest from "@/views/guest/components/ComAddGuest.vue"
const dialogRef = inject('dialogRef')
const loading=ref(false)
const data =ref({})
const working_day = moment(window.current_working_date).toDate()
const property = JSON.parse(localStorage.getItem("edoor_property"))
const gv = inject('$gv');
const toast = useToast();
const dialog = useDialog()
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
function onOK() {
    if(!data.value.guest){
        toast.add({ severity: 'warn', summary: "Add Desk Folio", detail: "Please select guest for add desk folio.", life: 5000 })
        return
    }
    
    loading.value = true
    var savedData = {
        name: data.value.name,
        posting_date: gv.dateApiFormat(data.value.posting_date),
        room_id: data.value.room_id,
        note: data.value.note,
        property: property.name,
        guest:data.value.guest
    }
    createUpdateDoc('Desk Folio',  savedData).then((r)=>{
        dialogRef.value.close(r)
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
}
function onClose(param = false) {
    dialogRef.value.close(param)
}
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
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
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
onMounted(()=> {
    // data.value.naming_series='FN.YYYY.-.####'; 
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    if(dialogRef.value.data.name){
        getDoc("Desk Folio", dialogRef.value.data.name).then(d=>{
            data.value = d
            data.value.posting_date = moment(d.posting_date).toDate()
        })

    }else {
        data.value.posting_date = moment(window.current_working_date).toDate()
    }
    if(window.isMobile){
    const elem = document.querySelector(".p-dialog");
		elem?.classList.add("p-dialog-maximized"); // adds the maximized class

 }
})
</script>