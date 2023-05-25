<template>
    <div class="flex night__btn_set h-12" :class="className">
        <Button class="border-start-0 w-3/12" @click="onDecrease" :disabled="(value <= 1)">-</Button>
        <div class="text-center bg-black text-white p-2 w-6/12">
            <div class="flex items-center justify-center w-full">
                <div>
                    <div style="line-height:.3">{{ value }}</div>
                    <div>Nights</div>
                </div>
            </div>
        </div>
        <Button class="border-end-0 w-3/12" @click="onIncrease">+</Button>
    </div>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({
    modelValue: Number,
    className: String
})
const emit = defineEmits(['update:modelValue', 'onUpdate'])
const value = computed({
    get() {
        return props.modelValue
    },
    set(newValue) {
        emit('update:modelValue', newValue)
        emit('onUpdate', newValue)
        return newValue
    }
})

function onIncrease() {
    value.value++

}
function onDecrease() {
    value.value--
}
</script>
<style lang="">
    
</style>