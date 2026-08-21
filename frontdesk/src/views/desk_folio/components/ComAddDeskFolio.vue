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
        <div class="col-6">
            <label>{{$t('Start Date')}}</label>
            <div>
                <Calendar selectOtherMonths class="w-full" showIcon v-model="data.start_date" @date-select="onDateSelect" :manualInput="false" :disabled="false" dateFormat="dd-mm-yy" :minDate="minDate"/>
            </div>
        </div> 
        <div class="col-6">
            <label>{{$t('End Date')}}</label>
            <div>
                <Calendar selectOtherMonths class="w-full" showIcon v-model="data.end_date" @date-select="onDateSelect" :manualInput="false" :disabled="false" dateFormat="dd-mm-yy" :minDate="endDate"/>
            </div>
        </div> 
        
        <div class="col-6">
            {{$t('Reference Number')}}
            <InputText type="text" class="p-inputtext-sm w-full" v-model="data.reference_number" :maxlength="100" />
        </div>
        <div class="col-6">
            <label >{{$t('Guest')}}<span class="text-red-500">*</span></label>
            <ComAutoComplete v-model="data.guest" placeholder="Select Guest" doctype="Customer" :isAddNew="true" @onAddNew="onAddNewGuest"
                class="auto__Com_Cus w-full"/>
        </div>
        <div class="col-6">
            <label >{{$t('Business Source')}}<span class="text-red-500">*</span></label>
            <ComAutoComplete v-model="data.business_source" placeholder="Select Business Source" doctype="Business Source"  
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
import { ref, inject, onMounted, getDoc, createUpdateDoc,useToast,useDialog,computed } from '@/plugin'
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


const minDate = ref(working_day)
const onDateSelect = (e) => {
    let start_date = moment(data.value.start_date).format("YYYY-MM-DD")

    let startDate = moment(start_date).toDate()

    let end_date = moment(data.value.end_date).format("YYYY-MM-DD")
    let endDate = moment(end_date).toDate()


    if (startDate >= endDate) {
        data.value.end_date = moment(data.value.start_date).add(1, 'days').toDate()
    }
}

const endDate = computed(() => {
    return moment(data.value.start_date).add(1, "days").toDate();
})


function onOK() {
    if(!data.value.guest){
        toast.add({ severity: 'warn', summary: "Add Desk Folio", detail: "Please select guest for add desk folio.", life: 5000 })
        return
    }
    
    loading.value = true
    var savedData = {
        name: data.value.name,
        reference_number: data.value.reference_number,
        posting_date: gv.dateApiFormat(data.value.posting_date),
        start_date: gv.dateApiFormat(data.value.start_date),
        end_date: gv.dateApiFormat(data.value.end_date),
        room_id: data.value.room_id,
        note: data.value.note,
        business_source:data.value.business_source,
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
            data.value.start_date = moment(d.start_date).toDate()
            data.value.end_date = moment(d.end_date).toDate()
        })

    }else {
        data.value.posting_date = moment(window.current_working_date).toDate()
        data.value.start_date = moment(window.current_working_date).toDate()
        data.value.end_date = moment(window.current_working_date).toDate()
    }
    if(window.isMobile){
    const elem = document.querySelector(".p-dialog");
		elem?.classList.add("p-dialog-maximized"); // adds the maximized class

 }
})
</script>