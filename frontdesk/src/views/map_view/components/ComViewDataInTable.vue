<template>
     <DataTable :value="data" tableStyle="min-width: 50rem" scrollable scrollHeight="600px" :virtualScrollerOptions="{ itemSize: 46 }">
      <Column v-for="col of columns" :key="col.fieldname" :field="col.fieldname" 
      :header="col.label"
         :headerClass="getAlignment(col.fieldtype)" 
         :bodyClass="getAlignment(col.fieldtype)"
         sortable 
      >
        <template #body="slotProps">
          
          <CurrencyFormat v-if="col.fieldtype=='Currency'" :value="slotProps.data[col.fieldname]"  :class="slotProps.data.is_total_row ==1?'font-bold':''"/>
         
            <span  v-else-if="col.fieldtype=='Percent'"  :class="slotProps.data.is_total_row ==1?'font-bold':''">{{ parseFloat(slotProps.data[col.fieldname]).toFixed(2)}}% </span>
          
          <span :class="slotProps.data.is_total_row ==1?'font-bold':''" v-else>
            {{slotProps.data[col.fieldname]}}
          </span>
        </template>
      </Column>
  </DataTable>

</template>
<script setup>
import { ref,inject } from "@/plugin"
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
const moment = inject("$moment");
 

const props = defineProps({
    filters:Object,
    columns:Object,
    data:Object
})

const emit = defineEmits(['update:modelValue','onSelect'])

function getAlignment(fieldtype){
  if (fieldtype=='Currency') return "text-right"
  if (fieldtype=='Percent' || fieldtype=='Int' || fieldtype=='Float') return "text-center"

  return "text-left" 
}


function onRefreshData(){
    emit("onFilter",props.filters)
}

</script>