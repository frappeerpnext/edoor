<template>
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading"> 
        <div class="mb-3">
            <div class="flex justify-center items-center">
                <ComUploadProfile doctype="Drivers" :docname="driver.name" :path="driver.photo" v-model="driver.photo"
                    @getFileName="onGetFile" />
            </div>
        </div>
        <ComReservationStayPanel class="mb-3" title="Driver Information">
            <template #content>
                <div class="grid">
                    <div class="col-12 lg:col-10 pt-2">
                        <label>Driver Name<span class="text-red-500">*</span></label><br />
                        <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="Driver Name"
                            v-model="driver.driver_name" :maxlength="50" />
                    </div>

                    <div class="col-12 lg:col-2  pt-2">
                        <label>Gender</label><br />
                        <Dropdown v-model="driver.gender" :options="optionGender" placeholder="Gender" class="w-full" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel class="mb-3" title="Contact Information">
            <template #content>
                <div class="grid">
                    <div class="col-12 lg:col-6 pt-2">
                        <label>Phone Number 1</label><br />
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                            v-model="driver.phone_number" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6 pt-2">
                        <label>Phone Number 2</label><br />
                        <InputText  type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                            v-model="driver.phone_number_2" :maxlength="50" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel class="mb-3" title="Identity Information">
            <template #content>
                <div class="grid">

                    <div class="col-12 lg:col-6  pt-1">
                        <label class="white-space-nowrap">Driver License Code</label><br />
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Driver License Code"
                            v-model="driver.driver_license_code" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6  pt-1">
                        <label>ID Expire Date</label><br />
                        <Calendar inputClass="w-full" class="p-inputtext-sm w-full" v-model="driver.expired_date" showIcon showButtonBar placeholder="ID Expire Date" dateFormat="dd-mm-yy" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Address & Note">
            <template #content>
                <div class="grid">
                    <div class="col-12  pt-1">
                        <label class="white-space-nowrap">Address</label><br />
                        <Textarea class="p-inputtext-sm w-full" placeholder="Address" v-model="driver.address" rows="4" />
                    </div>
                    <!-- <div class="col-12 lg:col-6 pt-1">
                        <label class="white-space-nowrap">Note</label><br />
                        <Textarea class="p-inputtext-sm w-full" placeholder="Note" v-model="driver.note" rows="4" />
                    </div> -->
                </div>
            </template>
        </ComReservationStayPanel>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, createUpdateDoc, onMounted, getDoc } from '@/plugin'
import ComDialogContent from '../../../components/form/ComDialogContent.vue';
import ComReservationStayPanel from '../../reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject('dialogRef')
let loading = ref(false)
const driver = ref({gender: 'Not Set'})
const optionGender = ref(['Not Set', 'Male', 'Female'])
const gv = inject('$gv')
const rs = inject('$reservation_stay');
const moment = inject('$moment');
function onClose(param = false) {
    dialogRef.value.close(param)
}
function onGetFile(file) {
    driver.value.file_name = file
}
function onOK() {
    loading.value = true
    var data = JSON.parse(JSON.stringify(driver.value))
    if(driver.value.expired_date)
        data.expired_date =  gv.dateApiFormat(driver.value.expired_date)
    else
        data.expired_date = ''
    createUpdateDoc('Drivers', { data: data }).then((r) => {
        onClose(r)
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}
onMounted(() => {
    if(dialogRef.value.data && dialogRef.value.data.drivername){
        getDoc("Drivers", dialogRef.value.data.drivername).then((r)=>{
            driver.value = r
            driver.value.expired_date = moment(r.expired_date).toDate()
        })
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