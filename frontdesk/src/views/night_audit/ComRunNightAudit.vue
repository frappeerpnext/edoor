<template>
    <ComNightAuditWelcome v-if="condition"/>
</template>
<script setup>
import { ref } from '@/plugin';
import ComNightAuditWelcome from "@/views/night_audit/components/ComNightAuditWelcome.vue"
const currentStep  = ref({})
const step = ref([
    {label:"Welcome", is_selected:true},
    {label:"Welcome", is_selected:true},

])
</script>