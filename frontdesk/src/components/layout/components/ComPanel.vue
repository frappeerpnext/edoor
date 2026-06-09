<template>
    <div :class="[customClass, borderRounded, 'bg-white p-2']">
        <div v-if="title || viewAll" :class="viewAll ? 'flex align-items-center justify-content-between' : ''">
            <div v-if="title" class="font-semibold text-lg px-1" :class="titleClass">
                {{ $t(title) }}
            </div>
            <template v-if="viewAll">
                <slot name="viewAll"></slot>
            </template>
        </div>
        <di class="h-full">
            <slot></slot>
        </di>
    </div>
</template>
<script setup>
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    title: String,
    customClass: String,
    borderRounded: {
        type: [String, Number, Object],
        default: "border-round-xl"
    },
    titleClass: String,
    viewAll: Boolean
})
</script>
