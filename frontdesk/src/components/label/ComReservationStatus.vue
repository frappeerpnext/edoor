<template>
    <span v-if="status" class="rounded-pill py-1 px-2 text-white border-round-3xl" :class="class"  :style="{ background: status?.color}">
        {{ $t(status.name ?? '') }}
        <slot>
        </slot>
    </span>
</template>
<script setup>
import {computed} from 'vue'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
    statusName: String,
    class: String
})
const setting = JSON.parse(localStorage.getItem('edoor_setting'))

const status = computed(()=>{
    return setting.reservation_status.find((r)=>r.name == props.statusName)
})

</script>
<style lang="">
    
</style>