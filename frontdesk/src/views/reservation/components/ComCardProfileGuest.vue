<template>
<div>
   <div class="flex items-center" >
      <div @click="onClick"  class="flex-none avatar-guest cursor-pointer">
         <ComAvatar :image="photo" :colorStatus="colorStatus" />
      </div>
      <div class="flex-grow-1 overflow-hidden">
         <div @click="onClick"   v-tooltip.top="name" class="font-semibold overflow-hidden text-overflow-ellipsis whitespace-nowrap color-purple-edoor cursor-pointer" >{{ name }}</div>
         <div v-tooltip.top="phoneNumber1" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap" > {{  phoneNumber1 ?? "No phone number" }}</div>
         <div v-tooltip.top="email" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap" >{{ email ?? "No email" }}</div>
      </div>
      <div class="flex-none" v-if="$slots.end">
         <slot name="end"></slot>
      </div>
   </div>
   <div class="grid gap-2 mt-2 ps-2">
      <span v-if=" moment(dob).format('DD-MM') == moment().format('DD-MM')" class="bg-green-bt p-2 rounded-xl flex justify-center items-center w-2rem h-2rem">
         <ComIcon icon="BirthdayIcon" class="w-1rem"></ComIcon>
      </span>
      <span v-badge.warning="2" class="bg-yellow-tran p-2 rounded-xl flex justify-center items-center w-2rem h-2rem p-overlay-badge cus-badge-a">
         <i  class="pi pi-car" style="font-size: 1rem"></i>
      </span>
   </div>
</div>
</template>
<script setup>
import {computed , inject} from '@/plugin'
import ComIcon from '../../../components/ComIcon.vue';
const moment = inject("$moment")
const emits = defineEmits(["onClick"])
const props = defineProps({
   name: String,
   phoneNumber1:String,
   phoneNumber2:String,
   email:String,
   dob:String,
   photo:String,
   transportation:String,
   colorStatus:String
})
const phoneNumber = computed(()=>{
   if(props.phoneNumber1 && props.phoneNumber2){
      return `${props.phoneNumber1} / ${props.phoneNumber2}`
   }
   return props.phoneNumber1 || props.phoneNumber2
})

const onClick=()=>{
   emits("onClick")
}
</script>
<style scoped>
.bg-green-bt{
   background: #c1e9e1;
}
.bg-yellow-tran{
   background: #f2e1ca;
}
.p-badge-no-gutter{
font-size: 0.7rem;
height: 1rem;
line-height: 1rem;
}
</style>