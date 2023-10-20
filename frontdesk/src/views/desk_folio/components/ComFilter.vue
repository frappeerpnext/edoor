<template>
    <span class="p-input-icon-left w-full mb-3">
        <i class="pi pi-search" />
        
        <InputText v-model="filter.search_field" placeholder="Search" class="w-full" />
    </span>
</template>
<script setup>
import {ref} from "@/plugin"
const filter = ref({})
</script>