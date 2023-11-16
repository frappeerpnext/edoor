<template>
    <!-- {{ rs }} -->
    <ComDialogContent @onClose="onClose" @onOK="onOK" :loading="loading">

        <div class="mb-3">
            <div class="flex justify-center items-center flex-col">
                <ComUploadProfile @loadingChange="updateLoadingStatus" @getFileName="refreshGuestDetail" doctype="Customer"
                    :docname="guest.name" :path="guest.photo" v-model="guest.attach" />
            </div>
        </div>
        <ComReservationStayPanel class="mb-3" title="Guest Information">
            <template #content>
                <div class="grid">
                    <div class="col-12 pt-2">
                        <label>Guest Name<span class="text-red-500">*</span></label><br />
                        <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="Guest Name"
                            v-model="guest.customer_name_en" :maxlength="50" />
                    </div>
                    <div class="col-12 pt-2">
                        <label>Company</label><br />
                        <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="Company"
                            v-model="guest.company_name" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6 xl:col-4 pt-2">
                        <label>Guest Type<span class="text-red-500">*</span></label><br />
                        <ComAutoComplete v-model="guest.customer_group" class="w-full" placeholder="Guest Type"
                            doctype="Customer Group" />
                    </div>
                    <div class="col-12 lg:col-6 pt-2">
                        <label>Province</label><br />
                        <ComAutoComplete v-model="guest.province" class="w-full" placeholder="province" doctype="Province" />
                    </div>
                    <div class="col-12 lg:col-6 xl:col-4 pt-2">
                        <label>Gender</label><br />
                        <Dropdown v-model="guest.gender" :options="optionGender" placeholder="Gender" class="w-full" />
                    </div>
                    
                    <div class="col-12 lg:col-6 xl:col-4 pt-2">
                        <label>Date of birth</label><br />
                        <Calendar class="p-inputtext-sm w-full" v-model="guest.date_of_birth" placeholder="Date of birth"
                            showIcon showButtonBar dateFormat="dd-mm-yy" :selectOtherMonths="true" />
                    </div>
                    
                    <!-- guest.date_of_birth -->
                    <div class="col-12 lg:col-6 xl:col-4 pt-2">
                        <label class="opacity-0">Disabled</label><br />
                        <div class="flex align-items-center">
                            <Checkbox class="mr-1" v-model="guest.disabled" :binary="true" :false-value="0" :trueValue="1"
                                inputId="disabled" />
                            <label for="disabled"> Disabled</label>
                        </div>
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
                            v-model="guest.phone_number" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6 pt-2">
                        <label>Phone Number 2</label><br />
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                            v-model="guest.phone_number_2" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6 pt-2">
                        <label>Email address</label><br />
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Email address"
                            v-model="guest.email_address" :maxlength="50" />
                    </div>
                    <div class="col-12 lg:col-6 pt-2">
                        <label>Country</label><br />
                        <ComAutoComplete v-model="guest.country" class="w-full" placeholder="Country" doctype="Country" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel class="mb-3" title="Identity Information">
            <template #content>
                <div class="grid">
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
                            placeholder="ID Expire Date" dateFormat="dd-mm-yy" showButtonBar showIcon />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Address & Note">
            <template #content>
                <div class="grid">
                    <div class="col-12 lg:col-6 pt-1">
                        <label class="white-space-nowrap">Address</label><br />
                        <Textarea class="p-inputtext-sm w-full" placeholder="Address" v-model="guest.address" rows="4" />
                    </div>
                    <div class="col-12 lg:col-6 pt-1">
                        <label class="white-space-nowrap">Note</label><br />
                        <Textarea class="p-inputtext-sm w-full" placeholder="Note" v-model="guest.note" rows="4" />
                    </div>
                </div>
            </template>
        </ComReservationStayPanel>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted, getApi, getDoc, createUpdateDoc } from '@/plugin'
import ComDialogContent from '@/components/form/ComDialogContent.vue';
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import Calendar from 'primevue/calendar';
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
let loading = ref(false)
const guest = ref({})
const optionGender = ref()
const moment = inject('$moment')



function onLoad() {
    loading.value = true
    getDoc('Customer', dialogRef.value.data.name)
        .then((doc) => {
            guest.value = doc
            guest.value.date_of_birth = doc.date_of_birth ? moment(doc.date_of_birth).toDate() : ''
            guest.value.expired_date = doc.expired_date ? moment(doc.expired_date).toDate() : ''
            loading.value = false
        })
        .catch((error) => {
            loading.value = false
        });
}

function onClose(param = false) {
    dialogRef.value.close(param)
}

function getMeta() {
    getApi('frontdesk.get_meta', {
        doctype: 'Customer'
    }).then((r) => {
        if (r.message) {
            const options = r.message.fields.find((r) => r.fieldname == 'gender')
            optionGender.value = options.options.split('\n')
            guest.value.gender = options.default
        }
    })
}

function onOK() {
    if (!guest.value.customer_name_en) {
        gv.toast('warn', 'Guest name is required.')
        return
    }
    else if (!guest.value.customer_group) {
        gv.toast('warn', 'Guest type is required.')
        return
    }
    loading.value = true
    var data = JSON.parse(JSON.stringify(guest.value))
    data.date_of_birth = data.date_of_birth ? moment(data.date_of_birth).format("YYYY-MM-DD") : ''
    data.expired_date = data.expired_date ? moment(data.expired_date).format("YYYY-MM-DD") : ''
    data.photo = data.attach
    createUpdateDoc('Customer', { data: data }, '', false)
    .then((r) => {
        window.socket.emit("ReservationList", { property: window.property_name })
        window.socket.emit("ReservationStayList", { property: window.property_name })
        window.socket.emit("Housekeeping", { property: window.property_name })
        window.socket.emit("Frontdesk", window.property_name)
        window.socket.emit("ComGuestLedger", { property: window.property_name })
        window.socket.emit("GuestDetail", window.property_name)
        window.socket.emit("Dashboard", window.property_name)
        window.socket.emit("ComIframeModal", window.property_name)
        window.socket.emit("GuestList", window.property_name)
        window.socket.emit("GuestLedgerTransaction", { property:window.property_name})
        window.socket.emit("Reports", window.property_name)
        window.socket.emit("FolioTransactionList", window.property_name)

        if (window.reservation_stay) {
            window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
        }
        if (window.reservation) {
            window.socket.emit("ReservationDetail", window.reservation)
        }
        onClose(r)
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}

const updateLoadingStatus = (isLoading) => {
    loading.value = isLoading;
};

onMounted(() => {
    getMeta()
    if (dialogRef.value.data.name) {
        onLoad()
    }else {
        //whenn add new guest check if have default guest name
        guest.value.customer_name_en = dialogRef.value.data.guest_name || ""
    }
})
</script>
<style>
.autocomplete-full-with input,
.autocomplete-full-with {
    width: 100%;
    display: block;
}</style>