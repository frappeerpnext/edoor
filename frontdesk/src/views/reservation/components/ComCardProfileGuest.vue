<template>
   <div class="flex items-center" >
      <div class="flex-none">
         <ComAvatar :image="photo"/>
      </div>
      <div class="flex-grow-1">
         <span class="font-bold" >{{ name }}</span>
         <div> {{ phoneNumber ?? "No phone number" }}</div>
         <div>{{ email ?? "No email" }}</div>
      </div>
   </div>
</template>
<script setup>
import {computed} from 'vue'
const props = defineProps({
   name: String,
   phoneNumber1:String,
   phoneNumber2:String,
   email:String,
   photo:String
})
const phoneNumber = computed(()=>{
   if(props.phoneNumber1 && props.phoneNumber2){
      return `${props.phoneNumber1} / ${props.phoneNumber2}`
   }
   return props.phoneNumber1 || props.phoneNumber2
})
</script>