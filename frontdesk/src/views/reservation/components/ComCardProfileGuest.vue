<template>
   <div class="flex items-center" >
      <div class="flex-none avatar-guest">
         <ComAvatar :image="photo" :colorStatus="colorStatus" />
      </div>
      <div class="flex-grow-1 overflow-hidden">
         <div  v-tooltip.top="name" class="font-bold overflow-hidden text-overflow-ellipsis whitespace-nowrap color-purple-edoor" >{{ name }}</div>
         <div v-tooltip.top="phoneNumber" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap" > {{ phoneNumber ?? "No phone number" }}</div>
         <div v-tooltip.top="email" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap" >{{ email ?? "No email" }}</div>
      </div>
      <div class="flex-none" v-if="$slots.end">
         <slot name="end"></slot>
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
   photo:String,
   colorStatus:String
})
const phoneNumber = computed(()=>{
   if(props.phoneNumber1 && props.phoneNumber2){
      return `${props.phoneNumber1} / ${props.phoneNumber2}`
   }
   return props.phoneNumber1 || props.phoneNumber2
})
</script>