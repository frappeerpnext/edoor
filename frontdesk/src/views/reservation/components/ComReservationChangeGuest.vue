<template>
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading">
        <div> 
            <div class="flex flex-col items-center mb-2">
                <div class="col-12">
                    <ComAutoComplete doctype="Customer" @onSelected="onSelected" isFull isIconSearch
                        placeholder="Search guest" />
                </div>
                <div class="col-12" v-if="!dialogRef.data.is_change_additional_guest">
                    <div class="flex">
                        <div class="flex align-items-center px-2">
                            <Checkbox v-model="isApplyAllStays" :binary="true" inputId="checkapplyall" />
                            <label for="checkapplyall"> {{ $t('Apply all stays') }}  ({{ rs.reservationStayNames.length}})</label>
                        </div>
                        <div class="flex align-items-center px-2" v-if="dialogRef.data.is_change_stay_guest">
                            <Checkbox v-model="isApplyMasterGuest" :binary="true" inputId="checkmasterguest" />
                            <label for="checkmasterguest"> {{ $t('Apply Master Guest') }}</label>
                        </div>
                    </div>
                </div>
            </div>
            <div> 
                <ComReservationStayPanel title="Guest Information">
                    <template #content>
                        <div class="grid">
                            <div class="col-12 pt-2">
                                <label>{{ $t('New Guest Name') }}<span class="text-red-500">*</span></label><br />
                                <InputText type="text" class="p-inputtext-sm h-12 w-full" :placeholder="$t('New Guest Name')"
                                    v-model="guest.customer_name_en" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                <label>{{ $t('Guest Type') }}<span class="text-red-500">*</span></label><br />
                                <ComAutoComplete v-model="guest.customer_group" class="w-full" placeholder="Guest Type"
                                    doctype="Customer Group" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                <label>{{ $t('Gender') }}</label><br />
                                <Dropdown v-model="guest.gender" :options="genderList" :placeholder="$t('Gender')" class="w-full" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                <label>{{ $t('Country') }}</label><br />
                                <ComAutoComplete v-model="guest.country" class="w-full" placeholder="Country"
                                    doctype="Country" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label>{{ $t('Phone Number') }}</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" :placeholder="$t('Phone Number')"
                                    v-model="guest.phone_number" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-8 pt-1">
                                <label>{{ $t('Email Address') }}</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" :placeholder="$t('Email Address')"
                                    v-model="guest.email_address" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label>{{ $t('Identity Type') }}</label><br />
                                <ComAutoComplete v-model="guest.identity_type" class="w-full" placeholder="Identity Type"
                                    doctype="Identity Type" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label class="white-space-nowrap">{{ $t('ID/Passport Number') }}</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" :placeholder="$t('ID/Passport Number') "
                                    v-model="guest.id_card_number" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label>{{ $t('ID Expire Date') }}</label><br />
                                <Calendar :selectOtherMonths="true" class="p-inputtext-sm w-full" v-model="guest.expired_date"
                                    :placeholder="$t('ID Expire Date')" dateFormat="dd-mm-yy" />
                            </div>
                        </div>
                    </template>
                </ComReservationStayPanel>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted, getApi,getDoc } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComDialogContent from '@/components/form/ComDialogContent.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const dialogRef = inject('dialogRef')
const rs = inject('$reservation_stay');
const gv = inject('$gv');
const moment = inject("$moment")


const genderList = ref(["Not Set", "Male", "Female"])
let isApplyAllStays = ref(false)
let isApplyMasterGuest = ref(false)
let loading = ref(false)
const guest = ref({})

 
function onSelected(r) {
    
    if(r.value){
        loading.value = true
        getDoc('Customer', r.value)
        .then((doc) => {
            guest.value = doc
            guest.value.expired_date = moment(guest.value.expired_date ).toDate()

            loading.value = false
        })
        .catch((error) => {
            loading.value = false
        });
    }
    else{
        guest.value = {}
    }
}
function onAdditionalSave(){
    loading.value = true
    if(!guest.value.name){
        guest.value.doctype = 'Customer'
    }
    const saveGuest = JSON.parse(JSON.stringify(guest.value))
    saveGuest.expired_date = moment(saveGuest.expired_date).format("YYYY-MM-DD")
    getApi('reservation.change_reservation_additional_guest',{ 
        reservation_stay: rs.reservationStay.name,
        guest: saveGuest,
    }).then((r) => {
        if (r) { 
            window.postMessage({action:"ReservationStayDetail"},"*")
            window.postMessage({action:"ReservationDetail"},"*")
            dialogRef.value.close()
            window.postMessage({action:"Reports"},"*") 
            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"ReservationList"},"*")
            
        }
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
}
function onClose(){
    dialogRef.value.close(false)
}
function onOK(){
    if(dialogRef.value.data.is_change_additional_guest){
        onAdditionalSave()
    }else{ 
        onStayGuestSave()
    }
}
function onStayGuestSave() {

    loading.value = true 
    if (rs.reservation.name) {
        if (!guest.value.doctype) {
            guest.value.doctype = 'Customer'
        }
        const saveGuest = JSON.parse(JSON.stringify(guest.value))
    saveGuest.expired_date = moment(saveGuest.expired_date).format("YYYY-MM-DD")

        getApi("reservation.change_reservation_guest", {
            reservation: rs.reservation.name,
            reservation_stay: rs.reservationStay.name,
            guest: saveGuest,
            is_apply_all_stays: isApplyAllStays.value,
            is_apply_master_guest: isApplyMasterGuest.value,
            is_only_master_guest: (isApplyMasterGuest.value && !isApplyAllStays.value)
        }).then((r)=>{
            loading.value = false
            if (r){
                window.postMessage({action:"ReservationStayDetail"},"*")
                window.postMessage({action:"ReservationDetail"},"*")
                window.postMessage({"action":"Frontdesk"},"*")
                dialogRef.value.close(r);
                window.postMessage({action:"ReservationStayList"},"*")
                window.postMessage({action:"ReservationList"},"*")
                window.postMessage({action:"Reports"},"*")
            }
        }).catch(()=>{
            loading.value = false
        })
    } else {
        gv.toast('error','Cannot get reservation name / guest name')
        loading.value = false
    }

}

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    if (dialogRef.value.data.is_change_master_guest) {
        isApplyMasterGuest.value = true
    }
})

</script>
<style>
.autocomplete-full-with input,
.autocomplete-full-with {
    width: 100%;
    display: block;
}
</style>