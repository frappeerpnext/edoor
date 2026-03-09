<template>
    <div class="grid px-2 pt-3">
<img  class="border-round-xl" :src="data.flag"/>
    </div>
    <table class="">
        <tr class="border-bottom-1 border-white-alpha-10" v-for="(c, index) in columns" :key="index">
<td class="pb-1">
 {{c.label}}
</td>
<td>
    <span class="me-2">:</span>
<template v-if="c.fieldtype==='Currency'">
      <CurrencyFormat :value="data[c.fieldname]" />
</template>
<template v-else-if="c.fieldtype==='Percent'">
{{ data[c.fieldname].toFixed(2)  }} %
</template>
<template v-else>
    {{data[c.fieldname]}}
</template>    
  
</td>
        </tr>
    </table>
    
</template>
<script setup>
import CurrencyFormat from "@/components/CurrencyFormat.vue"
const props = defineProps({
    data: Object,
    columns: Object,

})
</script>