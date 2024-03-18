<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
        <div class="grid">
            <div class="col-12">
                <ComReservationStayPanel title="Business Source Information">
                    <template #content>
                        <div class="grid">
                            <div class="col-6">
                                <label> {{ $t('Business Source') }} </label>
                                <InputText v-model="data.business_source" type="text" class="w-full"
                                    placeholder="Business Source" />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Business Source Type') }} </label>
                                <ComAutoComplete  class="w-full" v-model="data.business_source_type" placeholder="Business Source Type" doctype="Business Source Type" />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Country') }} </label>
                                <ComAutoComplete v-model="data.country" class="w-full" placeholder="Country"
                                    doctype="Country" />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('City') }} </label>
                                <InputText v-model="data.city" type="text" class="w-full" :placeholder=" $t('City') " />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Contact Name') }} </label>
                                <InputText v-model="data.contact_name" type="text" class="w-full"
                                    :placeholder=" $t('Contact Name') " />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Phone Number') }} </label>
                                <InputText v-model="data.phone_number" type="text" class="w-full"
                                    :placeholder=" $t('Phone Number') " />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Email') }} </label>
                                <InputText v-model="data.email" type="text" class="w-full" :placeholder=" $t('Email') " />
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
                                <label> {{ $t('Bank Name') }} </label>
                                <InputText v-model="data.bank_name" type="text" class="w-full" :placeholder=" $t('Bank Name') " />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Credit Card Number') }} </label>
                                <InputText v-model="data.credit_card_number" type="text" class="w-full"
                                    :placeholder=" $t('Credit Card Number') " />
                            </div>
                            <div class="col-6">
                                <label> {{ $t('Card Holder Name') }} </label>
                                <InputText v-model="data.card_holder_name" type="text" class="w-full"
                                    :placeholder=" $t('Card Holder Name') " />
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
                                <label for="ingredient1" class="ml-2"> {{ $t('Auto create City Ledger Account') }} </label>
                            </div>

                            <div class="col-12" v-if="data.auto_create_city_ledger_account">
                                <label> {{ $t('City Ledger Type') }} </label>
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
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

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
    createUpdateDoc("Business Source", data.value , '', rename).then((r) => {
        window.postMessage({action:"BusinessSource"},"*")
        window.postMessage({action:"ComBusinessSourceDetail"},"*")
        dialogRef.value.close(rename.new_name)
    }).catch((err) => {
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
    if (dialogRef.value.data.name) {
        onLoad()
    } else {
        data.value.property = window.property_name
    }
})
</script>