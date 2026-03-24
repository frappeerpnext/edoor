<template>
    <div class="bg-white p-2 border-round-xl" :class="class">
        <div :class="viewAll ? 'flex align-items-center justify-content-between' : ''">
            <div v-if="title" class="font-semibold text-lg px-1" :class="titleClass">
                {{ $t(title) }}
            </div>
            <template v-if="viewAll">
                <slot name="viewAll"></slot>
            </template>
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
    class: String,
    titleClass: String,
    viewAll: Boolean
})
</script>
