<template>
    <tr>
        <td class="w-auto" :class="[titleClass, isStyle]" :style="isBackground">
            <label class="font-normal white-space-nowrap" v-tippy="toolTipLabel">{{ $t(label ?? '') }}</label>
        </td>
        <td class="w-full" :class="[valueClass, isStyle]">
            <span v-if="isCurrency" class="font-semibold" v-tippy="toolTipValue">
                <CurrencyFormat :value="value" />
            </span>
            <span v-else class="font-semibold text-right" v-tippy="toolTipValue">{{ value }}</span>
            <div class="inline-grid" :class="{ 'ms-3': fill }">
                <slot></slot>
            </div>
        </td>
        
    </tr>
</template>
<script setup>
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
    label: String,
    value: [String, Number],
    toolTipLabel: [String, Number],
    toolTipValue: [String, Number],
    valueClass: String,
    titleClass: String,
    isCurrency: {
        type: Boolean,
        default: false
    },
    isStyle: {
        type: String,
        default: 'border-1 p-2'
    },
    isBackground: {
        type: String,
        default: 'background:rgb(243 243 243)'
    },
    fill: {
        type: Boolean,
        default: true
    }
})
</script>
<style></style>