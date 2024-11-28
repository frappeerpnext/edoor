<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="grid">
            <div class="col-5">
                <label>{{$t('Posting Date')}} </label>
                <Calendar disabled selectOtherMonths class="w-full" showIcon v-model="data.posting_date" :manualInput="false" :min-date="working_day" dateFormat="dd-mm-yy"/>
            </div>
           <div class="col-5">
            <label>{{ $t('Location') }}</label>
            <ComAutoComplete placeholder="Select Location"  v-model="data.location" class="pb-2 w-full"  doctype="Property Location"
            @onSelected="onSearch"  />
           </div>
           <div class="col-2">
                <label>{{ $t('Status') }}</label>
                <Dropdown v-model="data.status" optionLabel="label" optionValue="value" :options="status" placeholder="Status"
                                        class="w-full" />
           </div>
           <div class="col-12">
                <label>{{ $t('Note') }}</label>
                <Textarea v-model="data.note" rows="5" :placeholder="$t('Note')" cols="30"
                    class="w-full border-round-xl" />
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup >
import { ref, inject, createUpdateDoc, getApi, onMounted } from '@/plugin';
const property = JSON.parse(localStorage.getItem("edoor_property"))
import {i18n} from '@/i18n';
const dialogRef = inject('dialogRef');
const { t: $t } = i18n.global;
const moment = inject('$moment');
const status = ref([
    { label: $t('Lost'), value: 'Lost' },
    { label: $t('Found'), value: 'Found' }
]);
const data = ref({
    property : property.name,
    posting_date : moment().format('DD-MM-YYYY'),
})
getApi('frontdesk.get_working_day', {
    property: property.name
}).then((r) => {
   data.value.working_day = r.message.name
   data.value.working_date = r.message.date_working_day
   data.value.cashier_shift = r.message.cashier_shift.name
})
const loading = ref()


function onSave() {
    data.value.posting_date = moment().format('YYYY-MM-DD')
    loading.value = true
    createUpdateDoc('Lost and Found', data.value).then((r) => {
        dialogRef.value.close(r)
        window.postMessage("view_lost_and_found_detail" + "|" + r.message.name, '*')
    }).catch((err) => {
        loading.value = false
    })
}

</script>