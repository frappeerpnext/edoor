<template> 
    <div class="h-full">
        <ComPanel :title="$t('System Date')" class="sys-date bg text-white h-17rem md:h-full">
            <div class="text-center content_date">
                <div class="padding text-4xl">{{ $t(moment(data.working_date).format("dddd")) }}</div>
                <div class="padding day text-8xl">{{ moment(data.working_date).format("DD") }}</div>
                <div class="padding text-4xl white-space-nowrap">{{ $t(moment(data.working_date).format("MMMM")) }} {{ moment(data.working_date).format("yyyy") }}</div>
            </div>
        </ComPanel>
    </div>
</template>
<script setup>
import { inject } from 'vue'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const moment = inject("$moment")
const props = defineProps({
    data: Object
})
</script>
<style scoped>
.bg {
    background: #4d40ca !important;
}
.sys-date{
    position: relative;
}
.day {
    color: #ff5b00;
    line-height: 1;
}
.content_date{
position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    height: auto;    
}
.padding {
    padding: 0.2rem;
}

</style>