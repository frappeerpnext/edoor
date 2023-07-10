<template>
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading">
        {{ driver }}
        <div class="mb-3">
            <div class="flex justify-center items-center">
                <ComUploadProfile doctype="Drivers" :docname="driver.name" :path="driver.photo" v-model="driver.photo" @getFileName="onGetFile"/>
            </div>
        </div>
        <ComReservationStayPanel class="mb-3" title="Driver Information">
            <template #content>
                <div class="grid">
                    <div class="col-12 pt-2">
                        <label>Driver Name<span class="text-red-500">*</span></label><br />
                        <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="Driver Name"
                            v-model="driver.driver_name" :maxlength="50" />
                    </div>

                    <div class="col-12 lg:col-6 xl:col-4 pt-2">
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
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                            v-model="driver.phone_number_2" :maxlength="50" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel class="mb-3" title="Identity Information">
            <template #content>
                <div class="grid">

                    <div class="col-12 lg:col-6 xl:col-4 pt-1">
                        <label class="white-space-nowrap">Driver License Code</label><br />
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Driver License Code"
                            v-model="driver.driver_license_code" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6 xl:col-4 pt-1">
                        <label>ID Expire Date</label><br />
                        <Calendar class="p-inputtext-sm w-full" v-model="driver.expired_date" placeholder="ID Expire Date"
                            dateFormat="dd-mm-yy" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Address & Note">
            <template #content>
                <div class="grid">
                    <div class="col-12 lg:col-6 pt-1">
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
import { ref, inject,createUpdateDoc } from '@/plugin'
import ComDialogContent from '../../../components/form/ComDialogContent.vue';
import ComReservationStayPanel from '../../reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject('dialogRef')
let loading = ref(false)
const driver = ref({})
const optionGender = ref(['Not Set','Male','Female'])
const moment = inject('$moment')

function onClose(param = false) {
    dialogRef.value.close(param)
}
function onGetFile(file){
    driver.value.file_name = file
}
function onOK() { 
    loading.value = true
    var data = JSON.parse(JSON.stringify(driver.value))
    data.expired_date = moment(driver.value.expired_date).format('yyyy-MM-DD')
    createUpdateDoc('Drivers', {data:data}).then((r) => {
        onClose(r)
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}

</script>
<style>
.autocomplete-full-with input,
.autocomplete-full-with {
    width: 100%;
    display: block;
}
</style>