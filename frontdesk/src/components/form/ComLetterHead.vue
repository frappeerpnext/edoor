
<template>
    <div class="card flex justify-content-center">
        <Dropdown  v-model="selectedLetterhead" @change="onChange" :options="options"  placeholder="Letter Head" class="w-full " />
    </div>
</template>

<script setup>
import { ref,onMounted } from "vue";
const props = defineProps({
    letterhead:String
})

const emit = defineEmits(["onSelect"])
const selectedLetterhead = ref()
 
const options = ref(['No Letterhead'])
options.value = [...new Set(options.value.concat(window.setting.property.edoor_letterhead))]



function onChange(v){
    emit("onSelect", v.value)
}

onMounted(()=>{
 
    if(props.letterhead){
     
        selectedLetterhead.value = props.letterhead
       
    }else {
     
           selectedLetterhead.value = window.setting.property.default_letter_head
    }
    
})


</script>
