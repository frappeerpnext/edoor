
<template>
    <div class="card flex justify-content-center">
        <Dropdown v-model="selectedLetterhead" @change="onChange" :options="options"  placeholder="Letter Head" class="w-full md:w-14rem" />
    </div>
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(["onSelect"])
const selectedLetterhead = ref(
    window.setting.property.default_letter_head 
    )
 
const options = ref(['No Letterhead'])
options.value = [...new Set(options.value.concat(window.setting.property.edoor_letterhead))]



function onChange(v){
    emit("onSelect", v.value)
}


</script>
