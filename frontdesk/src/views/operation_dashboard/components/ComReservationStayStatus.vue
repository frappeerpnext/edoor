<template>
    <div class="px-3 py-1 text-white" :style="{background:data?.status_color,width:'fit-content','border-radius':'50px'}">
        {{ $t(data?.reservation_status) }}
    </div>
</template>
<script setup>
const props = defineProps({
    data:Object
})

import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
</script>