<template>
    <div>
        <div class="flex items-center mb-2">
            <div class="grow pr-2">
                <ComAutoComplete doctype="Customer" @onSelected="onSelected" isFull isIconSearch
                    placeholder="Search guest" />
            </div>
            <div class="flex-none" v-if="!dialogRef.data.is_change_additional_guest">
                <div class="flex">
                    <div class="flex align-items-center px-2">
                        <Checkbox v-model="isApplyAllStays" :binary="true" inputId="checkapplyall" />
                        <label for="checkapplyall"> Apply all stays ({{ dialogRef.data.total_reservation_stay }})</label>
                    </div>
                    <div class="flex align-items-center px-2" v-if="dialogRef.data.is_change_stay_guest">
                        <Checkbox v-model="isApplyMasterGuest" :binary="true" inputId="checkmasterguest" />
                        <label for="checkmasterguest"> Apply Master Guest</label>
                    </div>
                </div>
            </div>
        </div>
        <div>
            {{ dialogRef.data.reservation_stay }}
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
                            <Calendar class="p-inputtext-sm w-full" v-model="guest.expired_date"
                                placeholder="ID Expire Date" dateFormat="dd-mm-yy" />
                        </div>
                    </div>
                </template>
            </ComReservationStayPanel>
        </div>
        <div class="flex items-center justify-end pt-4">
            <Button label="OK" @click="onOK"></Button>
        </div>
    </div>
</template>
<script setup>
import { ref, inject, useToast, onMounted } from '@/plugin'
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const frappe = inject('$frappe')
const call = frappe.call()
const db = frappe.db()
const toast = useToast()
const dialogRef = inject('dialogRef')
const genderList = ref(["Not Set", "Male", "Female"])
let isApplyAllStays = ref(false)
let isApplyMasterGuest = ref(false)
const guest = ref({})
function onSelected(r) {
    if(r.value){
        db.getDoc('Customer', r.value)
        .then((doc) => {
            guest.value = doc
        })
        .catch((error) => console.error(error));
    }
    else{
        guest.value = {}
    }
}

function onAdditionalSave(){
    if(!guest.value.name){
        guest.value.doctype = 'Customer'
    }
    console.log(dialogRef.value.data.reservation_stay)
    call.get("edoor.api.reservation.change_reservation_additional_guest", { 
        reservation_stay: dialogRef.value.data.reservation_stay.name,
        guest: guest.value,
    }).then((result) => {
        if (result) {
            //dialogRef.value.close({ reservation_stay: result });
        }
    }).catch((error) =>{
        console.log(error)
    })
}
function onOK(){
    if(dialogRef.value.data.is_change_additional_guest){
        onAdditionalSave()
    }else{
        onStayGuestSave()
    }
}
function onStayGuestSave() {
    if (dialogRef.value.data.reservation.name) {
        if (!guest.value.doctype) {
            guest.value.doctype = 'Customer'
        }
        call.get("edoor.api.reservation.change_reservation_guest", {
            reservation: dialogRef.value.data.reservation.name,
            reservation_stay: dialogRef.value.data.reservation_stay.name,
            guest: guest.value,
            is_apply_all_stays: isApplyAllStays.value,
            is_apply_master_guest: isApplyMasterGuest.value,
            is_only_master_guest: (isApplyMasterGuest.value && !isApplyAllStays.value)
        }).then((result) => {
            if (result) {
                dialogRef.value.close({ guest: guest.value, is_guest_stay: (isApplyAllStays.value || dialogRef.value.data.is_change_stay_guest), is_master_guest: isApplyMasterGuest.value });
            }
        })
    } else {
        toast.add({ severity: 'error', summary: 'Cannot get reservation name / guest name', detail: '', life: 3000 });
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