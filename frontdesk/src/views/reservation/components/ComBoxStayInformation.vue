
<template>
  <span v-tippy="titleTooltip" v-if="title !== null" class=" text-right white-space-nowrap overflow-hidden text-overflow-ellipsis" :class="titleClass">{{ title }}</span>
  <div class="box-input py-2 px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white" style="background-color: #fff;" :class="valueClass">
    <span v-tippy="(value) ? '' : valueTooltip " :class="(isAction) ? 'link_line_action':''" @click="onClick" >
 
        <span v-if="isAction && !isSlot">
          <i v-if="!value && value != 0" class="pi pi-pencil"></i>
          {{ value || value == 0 ? value : '...' }}
        </span>
        <span v-else-if="isCurrency"><CurrencyFormat :value="value" /></span>
        <span v-else >{{ value }} </span>
        <slot></slot>
    </span>
  </div>
</template>
<script setup>
const emit = defineEmits(['onClick'])
const props = defineProps({
  titleClass:{type: String , default: 'col-2 mr-0'},
  valueTooltip:{type: String , default: null  },
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
  min-height: 35px;
  max-height: 35px;
}
</style>
