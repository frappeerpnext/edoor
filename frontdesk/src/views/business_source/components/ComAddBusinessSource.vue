<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
        <div class="grid">
            <div class="col-12">
                <ComReservationStayPanel title="Business Source Information">
                    <template #content>
                        <div class="grid">
                            <div class="col-6">
                                <label>Business Source</label>
                                <InputText v-model="data.business_source" type="text" class="w-full"
                                    placeholder="Business Source" />
                            </div>
                            <div class="col-6">
                                <label>Business Source Type</label>
                                <ComAutoComplete  class="w-full" v-model="data.business_source_type" placeholder="Business Source Type" doctype="Business Source Type" />
                            </div>
                            <div class="col-6">
                                <label>Country</label>
                                <ComAutoComplete v-model="data.country" class="w-full" placeholder="Country"
                                    doctype="Country" />
                            </div>
                            <div class="col-6">
                                <label>City</label>
                                <InputText v-model="data.city" type="text" class="w-full" placeholder="City" />
                            </div>
                            <div class="col-6">
                                <label>Contact Name</label>
                                <InputText v-model="data.contact_name" type="text" class="w-full"
                                    placeholder="Contact Name" />
                            </div>
                            <div class="col-6">
                                <label>Phone Number</label>
                                <InputText v-model="data.phone_number" type="text" class="w-full"
                                    placeholder="Phone Number" />
                            </div>
                            <div class="col-6">
                                <label>Email</label>
                                <InputText v-model="data.email" type="text" class="w-full" placeholder="Email" />
                            </div>
                        </div>
                    </template>
                </ComReservationStayPanel>
            </div>
            <div class="col-12">
                <ComReservationStayPanel title="Credit Card Information">
                    <template #content>
                        <div class="grid">
                            <div class="col-6">
                                <label>Bank Name</label>
                                <InputText v-model="data.bank_name" type="text" class="w-full" placeholder="Bank Name" />
                            </div>
                            <div class="col-6">
                                <label>Credit Card Number</label>
                                <InputText v-model="data.credit_card_number" type="text" class="w-full"
                                    placeholder="Credit Card Number" />
                            </div>
                            <div class="col-6">
                                <label>Card Holder Name</label>
                                <InputText v-model="data.card_holder_name" type="text" class="w-full"
                                    placeholder="Card Holder Name" />
                            </div>
                        </div>
                    </template>
                </ComReservationStayPanel>
            </div>
            <div class="col-12" v-if="dialogRef.data.is_city_ledger">
                <ComReservationStayPanel title="City Ledger Information">
                    <template #content>
                        <div class="grid">
                            <div class="col-12">
                                <Checkbox inputId="ingredient1" v-model="data.auto_create_city_ledger_account" :binary="true" />
                                <label for="ingredient1" class="ml-2"> Auto create City Ledger Account</label>
                            </div>

                            <div class="col-12" v-if="data.auto_create_city_ledger_account">
                                <label>City Ledger Type</label>
                                <ComAutoComplete isIconSearch v-model="data.city_ledger_type" class="w-full"
                                    placeholder="City Ledger Type" doctype="City Ledger Type" @onSelected="onSelectedCustomer" />
                            </div>
                        </div>
                    </template>
                </ComReservationStayPanel>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, createUpdateDoc, inject, getDoc, onMounted } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
const data = ref({})
const loading = ref(false)
const property = JSON.parse(localStorage.getItem("edoor_property"))
const checked = ref(false);

function onLoad() {
    loading.value = true
    getDoc('Business Source', dialogRef.value.data.name)
        .then((r) => {
            data.value = r
            loading.value = false
        })
        .catch((error) => {
            loading.value = false
        });
}

function onClose() {
    dialogRef.value.close()
}

function onSave() {
    if (!data.value.business_source) {
        gv.toast('warn', 'Bussiness source is required.')
        return
    }
    else if (!data.value.business_source_type) {
        gv.toast('warn', 'Bussiness source type is required.')
        return
    }
    loading.value = true
    const rename = {
        old_name: dialogRef.value.data.name,
        new_name: data.value.business_source
    }
    createUpdateDoc("Business Source", { data: data.value }, '', rename).then((r) => {
        window.socket.emit("ComBusinessSource",window.property_name)
        dialogRef.value.close(rename.new_name)
        onLoad()

    }).catch((err) => {
        loading.value = false
    })
}

onMounted(() => {
    if (dialogRef.value.data.name) {
        onLoad()
    } else {
        data.value.property = property.name
    }
})
</script>