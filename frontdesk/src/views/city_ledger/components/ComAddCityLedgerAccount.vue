<template> 
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="flex flex-col gap-3">
        <ComReservationStayPanel title="City Ledger Information">
            <template #content>
                <div class="grid">
                <div class="col-6">
                    <label>{{ $t('City Ledger Name') }} </label>
                    <InputText class="w-full" v-model="data.city_ledger_name" type="text" placeholder="City Ledger Name" :maxlength="50" />
                </div>
                <div class="col-6">
                    <label>{{ $t('City Ledger Type') }} </label>
                    <ComSelect class="w-full" v-model="data.city_ledger_type" placeholder="City Ledger Type" doctype="City Ledger Type" />
                </div>
                <div class="col-6">
                    <label>{{ $t('Business Source') }} </label>
                    <ComAutoComplete class="w-full" v-model="data.business_source" placeholder="Business Source" doctype="Business Source" />
                </div>
                <div class="col-6">
                    <label>{{ $t('Company Name') }} </label><br />
                    <InputText class="w-full" v-model="data.company_name" type="text"  placeholder="Company Name" :maxlength="50" />
                </div>  
                <div class="col-6">
                    <label>{{ $t('Phone Number') }}</label><br />
                    <InputText class="w-full" v-model="data.phone_number" type="text"  placeholder="Phone Number" :maxlength="50" />
                </div>
                <div class="col-6">
                    <label>{{ $t('Email Address') }} </label><br />
                    <InputText class="w-full" v-model="data.email_address" type="text"  placeholder="Email Address" :maxlength="50" />
                </div>
                <div class="col-12">
                    <label>{{ $t('Address') }} </label>
                    <div class="card flex justify-content-left">
                        <Textarea v-model="data.address"  rows="3"  style="width: 100%;" />
                    </div>
                </div> 
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Bank Information">
            <template #content>
                <div class="grid">
                    <div class="col-12">
                            <div class="w-50">
                            <label>{{ $t('Bank Name') }} </label><br />
                            <InputText class="w-full" v-model="data.bank_name" type="text"  placeholder="Bank Name" :maxlength="50" />
                            </div>
                        </div>  
                        <div class="col-6">
                            <label>{{ $t('Bank Account Number') }}</label><br />
                            <InputText class="w-full" v-model="data.bank_account_number" type="text"  placeholder="Bank Account Number" :maxlength="50" />
                        </div >
                        <div class="col-6">
                            <label>{{ $t('Bank Account Name') }} </label><br />
                            <InputText class="w-full" v-model="data.bank_account_name" type="text"  placeholder="Bank Account Name" :maxlength="50" />
                        </div>
                </div>
            </template>
        </ComReservationStayPanel>  
        <ComReservationStayPanel title="Contact Person Information">
            <template #content>
                <div class="grid">
                <div class="col-6">
                    <label>{{ $t('Contact Name') }} </label><br />
                    <InputText class="w-full" v-model="data.contact_name" type="text"  placeholder="Contact Name" :maxlength="50" />
                </div>
                <div class="col-6">
                    <label>{{ $t('Phone Number') }} </label><br />
                    <InputText class="w-full"  v-model="data.contact_phone_number" type="text"  placeholder="Phone Number" :maxlength="50" />
                </div>                
            
            </div>
        </template>
    </ComReservationStayPanel>  
    <ComReservationStayPanel title="Note">
        <template #content> 
            <div class="col-12 -mt-3 w-full px-0">
                    <div class="card flex justify-content-left">
                        <Textarea v-model="data.note"  rows="3"  style="width: 100%;" />
                    </div>
            </div>
        </template>
    </ComReservationStayPanel>
    </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, createUpdateDoc,inject,getDoc,onMounted } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
const loading = ref(false);
const property = JSON.parse(localStorage.getItem( "edoor_property"))
const data = ref({property:property.name})
function onClose(){
    dialogRef.value.close()
}

function onSave(){
    if(!data.value.city_ledger_name){
        gv.toast('warn','City ledger name is required.')
        return
    }
    else if(!data.value.city_ledger_type){
        gv.toast('warn','City ledger type is required.')
        return
    }
    loading.value = true
    createUpdateDoc("City Ledger", data.value)
    .then((r)=>{
        window.postMessage({action:"CityLedgerAccount"},"*")
        window.postMessage({action:"ComCityLedgerDetail"},"*")
        loading.value = false
        dialogRef.value.close(r)
        
    }).catch((err)=>{
        loading.value = false
    })
}
onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
  if(dialogRef.value.data.name){
    getDoc("City Ledger", dialogRef.value.data.name).then((r)=>{
      data.value = r
    })
  }
})
</script>