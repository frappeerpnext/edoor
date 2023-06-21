<template>
    <div>
        <SplitButton class="border-split-none" label="Mores" icon="pi pi-list" :model="items" />
    </div>
</template>
<script setup>
import { inject ,ref } from "@/plugin";
import ComAuditTrail from '../../../components/layout/components/ComAuditTrail.vue';
const emit = defineEmits('onAuditTrail')
const items=ref([])
items.value.push({
    label: "Audit Trail",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
items.value.push({
    label: "Allow post to City Ledger",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
items.value.push({
    label: "Edit Trail",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
items.value.push({
    label: "Edit Trail",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
</script>