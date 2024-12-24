<template>
    departure guest
</template>
<script setup>
 import { inject,ref, useRoute } from '@/plugin';
 const route = useRoute()
 const op = inject("$operation_dashboard")
    op.page_title = route.meta.title
</script>