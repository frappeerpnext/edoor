<template>
    <ComDocumentList doctype="Reservation Stay">
        <template #guest_name="{ item, index }">
           guest name
        </template>
    </ComDocumentList>
</template>
<script setup>
    import ComDocumentList from "@/components/document/ComDocumentList.vue"
</script>