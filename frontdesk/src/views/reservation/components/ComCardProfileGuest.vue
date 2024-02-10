<template>
<div>
   <div class="flex items-center" >
      <div @click="onClick"  class="flex-none avatar-guest cursor-pointer">
         <ComAvatar :image="photo" :colorStatus="colorStatus" avatarClass="mr-2"/>
      </div>
      <div class="flex-grow-1 overflow-hidden">
         <div @click="onClick"   v-tippy="name" class="font-semibold overflow-hidden text-overflow-ellipsis whitespace-nowrap color-purple-edoor cursor-pointer" >{{ name }}</div>
         <div v-tippy="phoneNumber1" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap" ><span v-html="phoneNumber1 ?? '<span class=\'font-italic text-gray-400\'>No phone number</span>'"></span></div>
         <div v-tippy="email" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap" > <span v-html="email ?? '<span class=\'font-italic text-gray-400\'>No email adress</span>'"></span></div>
      </div>
      <div class="flex-none" v-if="$slots.end">
         <slot name="end"></slot>
      </div>
   </div>
   <div class="grid gap-2 mt-2 ps-2">
      <span v-tippy="name + ' birthday at ' +moment(dob).format('DD-MM-yy')" v-if="dob && (moment(dob).format('DD-MM') == moment().format('DD-MM') || moment(dob).add(-1, 'day').format('DD-MM') == moment().format('DD-MM') )" class="bg-green-bt p-2 rounded-xl flex justify-center items-center w-2rem h-2rem">
         <ComIcon icon="BirthdayIcon" class="w-1rem"></ComIcon>
      </span>
      <slot name="footer"></slot>
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

</style>