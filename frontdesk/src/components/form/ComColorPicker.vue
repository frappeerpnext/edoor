<template>
    <ColorPicker
    theme="light"
    :color="color"
    :sucker-hide="true"
    :sucker-canvas="option.suckerCanvas"
    :sucker-area="option.suckerArea"
    @changeColor="changeColor"
  /> 
</template>
<script setup>
    import {computed} from 'vue'
    import { ColorPicker } from 'vue-color-kit'
    import 'vue-color-kit/dist/vue-color-kit.css'
    const emit = defineEmits(['update:modelValue'])
    const props = defineProps({
        modelValue: String
    })
    let color = computed({
        get(){
            return props.modelValue || "rgba(0,0,0,0)"
        },
        set(newValue){
            return newValue
        }
    })
    const option = {
        suckerCanvas: null,
        suckerArea: []
    }
    function changeColor(color){ 
        if (color && color.rgba.r == 0 && color.rgba.g == 0 && color.rgba.b == 0 && color.rgba.a == 0)
            emit('update:modelValue', "")
        else
            emit('update:modelValue', color.hex)
    }
</script>
<style>
    .hu-color-picker {
        width: 219px !important;
        box-shadow: none !important;
        margin: 0 !important
    }
    .color-type,.color-alpha{
        display: none !important;
    }
</style>