<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div>
            <div>
                <label>Room Number</label>
                <InputNumber v-model="doc.rooms" class="w-full"/>
            </div>
            <div>
                <label>Room Type</label>
                <ComAutoComplete v-model="doc.room_type" class="w-full" doctype="Room Type"/>
            </div>
            <div>
                <label>Date</label>
                <Calendar v-model="doc.date" class="w-full" dateFormat="dd-mm-yy" showIcon showButtonBar />
            </div>
            <div>
                <label>Rate Type</label>
                <ComSelect v-model="doc.rate_type" placeholder="Rate Type" doctype="Rate Type"
            class="auto__Com_Cus w-full" />
            </div>
            <div>
                <label>Rate</label>
                <InputNumber v-model="doc.rate" class="w-full"/>
            </div>
            <div>
                <label>Discount Type</label>
                <ComSelect class="w-full" id="dis_type" v-model="doc.discount_type" :options="['Percent', 'Amount']" :clear="false" />
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>

import { ref, inject, getDoc, computed, onMounted, nextTick,useToast } from "@/plugin"
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';

const gv = inject("$gv")

const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const doc = ref({
    discount_type:'Percent'
});
function onSave() {

}


</script>
