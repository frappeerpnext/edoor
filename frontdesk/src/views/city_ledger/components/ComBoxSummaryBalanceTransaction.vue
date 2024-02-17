<template>
 <div :class="[titleClass]" class="col flex flex-column rounded-lg grow p-2 shadow-charge-total  border">
                    
                    <div class="flex justify-content-between">
                     <span  class="text-500  text-sm text-end">
                                <span class="white-space-nowrap" v-if="des">
                                   {{ des }}
                                </span>
                               </span> 
                               <span class="text-500 uppercase text-sm text-end">{{label}}</span>  
                    </div>
                    
                    <div
                        class="text-xl line-height-2 font-semibold text-end">
                        <span :class="valueClass">
                            <CurrencyFormat v-if="isCurrency" :value="value" />
                            <template v-else>
                                {{ value }}
                            </template>
                        </span>
                    
                    </div> 
                </div>    
</template>
  
  <script setup>
  const props = defineProps({
    label: String,
    value: [String, Number],
    toolTipLabel: [String, Number],
    toolTipValue: [String, Number],
    valueClass: String,
    titleClass: String,
    des:String,
    isCurrency: {
        type: Boolean,
        default: false
    },
})
  </script>