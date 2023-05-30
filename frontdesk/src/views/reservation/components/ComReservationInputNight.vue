<template>
    <div class="night__btn_set" style="height: calc(100% - 19.5px);" :class="className">
        <div class="h-full grid m-0">
            <div class="col p-0 px-1">
                <Button class="w-full h-full justify-center" @click="onDecrease" :disabled="(value <= 1)">-</Button>
            </div>
            <div class="col-6 p-0">
                <div class="text-center bg-black text-white h-full border-round-xl">
                    <div class="flex items-center justify-center w-full h-full">
                        <div>
                            <div style="line-height:1">{{ value }} <br /> <span style="font-size:11px">Nights</span></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col p-0 px-1">
                <Button class="w-full h-full justify-center" @click="onIncrease">+</Button>
            </div>
        </div>
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