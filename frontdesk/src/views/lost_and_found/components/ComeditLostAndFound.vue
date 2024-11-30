<template>
    <ComDialogContent @onOK="onSave" :loading="loading" hideButtonClose>
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
import { ref, inject, updateDoc, getApi, onMounted } from '@/plugin';
const property = JSON.parse(localStorage.getItem("edoor_property"))
import {i18n} from '@/i18n';
const dialogRef = inject('dialogRef');
const { t: $t } = i18n.global;
const moment = inject('$moment');
const status = ref([
    { label: $t('Lost'), value: 'Lost' },
    { label: $t('Found'), value: 'Found' }
]);
const data = ref({})

const loading = ref(false)


function onSave() {
    loading.value = true
    updateDoc("Lost and Found",dialogRef.value.data.name , data.value).then(r=>{
        loading.value = false
        window.postMessage({"action":"LostAndFoundList"},"*") 
        dialogRef.value.close(r)
        }).catch(() => {
        loading.value = false    
        })
}
onMounted(() => {
    data.value.posting_date = dialogRef.value.data.posting_date
    data.value.location = dialogRef.value.data.location
    data.value.status = dialogRef.value.data.status
    data.value.note = dialogRef.value.data.note
});
</script>