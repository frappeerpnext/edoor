
<template>
  <span v-tippy="$t(titleTooltip ?? '')" v-if="title !== null" class=" text-right white-space-nowrap overflow-hidden text-overflow-ellipsis" :class="titleClass!=''?titleClass:'col-2 mr-0'">{{ $t(title ?? '') }}</span>
  <div class="box-input py-1 px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white" style="background-color: #fff;" :style="{maxWidth:valueMaxWidth}" :class="valueClass">
    <span v-tippy="(value) ? '' : valueTooltip " :class="(isAction) ? 'link_line_action overflow-hidden':''" @click="onClick" >
 
        <span v-if="isAction && !isSlot">
          <i v-if="!value && value != 0" class="pi pi-pencil"></i>
          {{ value || value == 0 ? value : '...' }}
        </span>
        <span v-else-if="isCurrency"><CurrencyFormat :value="value" /></span>
        <Checkbox v-else-if="isCheckbox" v-model="checked" :binary="true" :trueValue="1" :falseValue="0" @change="checked = 1"/>
        <span v-else >{{ $t(value ?? '') }} </span> 
        <slot></slot>
    </span>
  </div>
</template>
<script setup>
import {ref} from 'vue'
import {i18n} from '@/i18n';
const emit = defineEmits(['onClick'])
const { t: $t } = i18n.global;
const props = defineProps({
  titleClass:{type: String , default: ''},
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
  },
  valueMaxWidth: String,
  isCheckbox: {type: Boolean, default: false}
})
 
const checked = ref(1)
const  onClick=(event)=>{
 
  emit("onClick",event)
}

</script>
<style scoped>
.box-input{
  min-height: 30px;
  max-height: 30px;
}
</style>
