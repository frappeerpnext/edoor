<template>
    <div class="bg-white p-2 border-round-xl" :class="class">
        <div class="font-semibold text-lg px-1">
            {{ $t(title) }}
        </div>
        <div>
            <slot></slot>
        </div>
    </div>
</template>
<script setup>
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    title: String,
    class: String
})
</script>
