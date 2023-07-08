<template>
    <tr>
        <td class="border-1 p-2 w-auto">
            <label class="font-normal white-space-nowrap" v-tooltip.top="toolTipLabel">{{label}}</label>
        </td>
        <td class="w-full">
            <div class="flex gap-3">
                <span v-if="isCurrency" class="font-semibold" v-tooltip.top="toolTipValue">
                    <CurrencyFormat :value="value"/>
                </span>
                <span v-else class="font-semibold text-right" v-tooltip.top="toolTipValue">{{value}}</span>
                <span>
                    <slot></slot>
                </span>
            </div>
        </td>
    </tr>
</template>
<script setup>

const props = defineProps({
label: String,
value: [String, Number],
toolTipLabel: [String, Number],
toolTipValue: [String, Number],
valueClass: [String, Number],
isCurrency: {
    type: Boolean,
    default: false
}
})
</script>
<style>

</style>