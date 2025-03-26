<template>
    <form @submit.prevent="submitForm">
        <div class="p-input-icon-left w-full">
            <i class="pi pi-search" />
            <InputText class="w-full" v-model="filter.keyword" :placeholder="$t('Search')" @input="onSearch" />
        </div>
        <div class="flex align-items-center relative gap-2 my-2">
            <Checkbox v-model="filter.enable_date_filter" :binary="true" :trueValue="1" :falseValue="0" />

            <label class="font-medium cursor-pointer ">{{ $t('Posting Date') }}
            </label>

        </div>

        <div class="grid">
            <div class="col">
                <Calendar :selectOtherMonths="true" :disabled="!filter.enable_date_filter" v-model="filter.start_date"
                    class="w-full" dateFormat="dd-mm-yy" showIcon showButtonBar selectOtherMonths
                    panelClass="no-btn-clear" />
            </div>
            <div class="col">

                <Calendar :selectOtherMonths="true" :disabled="!filter.enable_date_filter" v-model="filter.end_date"
                    class="w-full" dateFormat="dd-mm-yy" showIcon showButtonBar selectOtherMonths
                    panelClass="no-btn-clear" />
            </div>
        </div>
        <h1 class="mt-2">City Ledger</h1>
        <ComAutoComplete v-model="filter.city_ledger" placeholder="Select City Ledger" doctype="City Ledger"
            class="auto__Com_Cus w-full" :pageLength="20" />
        <h1 class="mt-2">Payment Status</h1>
        <ComSelect :clear="false" :options="['All', 'Paid', 'Partialy Paid', 'Unpaid']" v-model="filter.payment_status" />
        <h1 class="mt-2">Status</h1>
        <ComSelect :clear="false" :options="['All', 'Open', 'Closed']" v-model="filter.status" />

        <Button class="mt-3 w-full" label="Search" type="submit" @click="onFilter" />
        <Button label="Clear Filter" class="mt-3 w-full" severity="warning" @click="onClearFilter" />
    </form>
</template>
<script setup>

import { ref, inject, getDoc, computed, onMounted, createUpdateDoc, getDocList, getApi, postApi, nextTick } from "@/plugin"
import Calendar from 'primevue/calendar';
import { i18n } from '@/i18n';
const emit = defineEmits()
const { t: $t } = i18n.global;
const moment = inject("$moment")


const filter = ref({
    start_date: moment(window.current_working_date).toDate(),
    end_date: moment(window.current_working_date).toDate(),
    keyword: "",
    city_ledger: "",
    payment_status: "All",
    status: "All"
})

function onFilter() {

    emit("onFilter", filter.value)
}

function onClearFilter() {
    filter.value =  {
        enable_date_filter: 0,
        keyword: "",
        city_ledger: "",
        payment_status: "All",
        status: "All"
    };
    emit("onFilter",filter.value)
}


</script>