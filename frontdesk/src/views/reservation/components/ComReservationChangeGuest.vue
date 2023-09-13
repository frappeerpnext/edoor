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
                            <label for="checkapplyall"> Apply all stays ({{ rs.reservationStayNames.length}})</label>
                        </div>
                        <div class="flex align-items-center px-2" v-if="dialogRef.data.is_change_stay_guest">
                            <Checkbox v-model="isApplyMasterGuest" :binary="true" inputId="checkmasterguest" />
                            <label for="checkmasterguest"> Apply Master Guest</label>
                        </div>
                    </div>
                </div>
            </div>
            <div> 
                <ComReservationStayPanel title="Guest Information">
                    <template #content>
                        <div class="grid">
                            <div class="col-12 pt-2">
                                <label>New Guest Name<span class="text-red-500">*</span></label><br />
                                <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="New Guest Name"
                                    v-model="guest.customer_name_en" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                <label>Guest Type<span class="text-red-500">*</span></label><br />
                                <ComAutoComplete v-model="guest.customer_group" class="w-full" placeholder="Guest Type"
                                    doctype="Customer Group" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                <label>Gender</label><br />
                                <Dropdown v-model="guest.gender" :options="genderList" placeholder="Gender" class="w-full" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                <label>Country</label><br />
                                <ComAutoComplete v-model="guest.country" class="w-full" placeholder="Country"
                                    doctype="Country" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label>Phone Number</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                                    v-model="guest.phone_number" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-8 pt-1">
                                <label>Email Address</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Email Address"
                                    v-model="guest.email_address" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label>Identity Type</label><br />
                                <ComAutoComplete v-model="guest.identity_type" class="w-full" placeholder="Identity Type"
                                    doctype="Identity Type" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label class="white-space-nowrap">ID/Passport Number</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="ID/Passport Number"
                                    v-model="guest.id_card_number" :maxlength="50" />
                            </div>
                            <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                <label>ID Expire Date</label><br />
                                <Calendar :selectOtherMonths="true" class="p-inputtext-sm w-full" v-model="guest.expired_date"
                                    placeholder="ID Expire Date" dateFormat="dd-mm-yy" />
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
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue'; 
import ComDialogContent from '../../../components/form/ComDialogContent.vue';
const dialogRef = inject('dialogRef')
const rs = inject('$reservation_stay');
const gv = inject('$gv');
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
    getApi('reservation.change_reservation_additional_guest',{ 
        reservation_stay: rs.reservationStay.name,
        guest: guest.value,
    }).then((r) => {
        if (r) { 
            rs.reservationStay = r.message.result
            dialogRef.value.close();
        }
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
        getApi("reservation.change_reservation_guest", {
            reservation: rs.reservation.name,
            reservation_stay: rs.reservationStay.name,
            guest: guest.value,
            is_apply_all_stays: isApplyAllStays.value,
            is_apply_master_guest: isApplyMasterGuest.value,
            is_only_master_guest: (isApplyMasterGuest.value && !isApplyAllStays.value)
        }).then((r)=>{
            if (r) {
                loading.value = false
                // if(isApplyAllStays.value || dialogRef.value.data.is_change_stay_guest){
                //     // is_guest_stay
                //     rs.guest = guest.value
                // }   
                // if(isApplyMasterGuest.value){
                //     // master guest
                //     rs.masterGuest = guest.value
                // }
                dialogRef.value.close(r);
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