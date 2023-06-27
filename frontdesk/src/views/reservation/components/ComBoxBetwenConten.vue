
<template>
    <label :for="inputIdFor" v-tooltip.top="titleTooltip" v-if="title !== null" class="cursor-pointer flex items-center justify-end text-right white-space-nowrap" :class="titleClass">{{ title }}</label>
    <div class="flex justify-between items-center box-input py-3 px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white" style="background-color: #fff;" :class="valueClass">
        <slot name="prefix"></slot>
        <slot name="default"></slot>
    </div>
  </template>
  <script setup>
  const emit = defineEmits(['onClick'])
  const props = defineProps({
    titleClass:{type: String , default: 'col-2 mr-0'},
  valueTooltip:{type: String , default: null  },
  inputIdFor:{type: String , default: null  },
  title: {type: String , default: null},
  isAction:{   type: Boolean,default: false},
  value: [String, Number],
  isSlot: {type: Boolean,default: false},
  valueClass: String,
  titleTooltip:String,
  isCurrency: {
    type: Boolean,
    default: false
  }
  })
   
  const  onClick=(event)=>{
   
    emit("onClick",event)
  }
  
  </script>
  <style scoped>
  .box-input{
    height: 38.5px !important;
    max-height: 38.5px !important;
  }
  </style>
  