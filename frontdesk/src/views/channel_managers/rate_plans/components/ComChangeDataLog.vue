<template>
  <ComDocumentList
    
    doctype="Change Data Log"
    title="Change Data Log"
    list_view_setting="rate_plan_change_data_log_list"
    :options="options"
     
  >
 
    <template #name="{ item, index }">
      <Button
        class="link_line_action1"
        link
        @click="onViewLog(item)"
      >
        {{ item.name }}
      </Button>
    </template>
 
     
  </ComDocumentList>
</template>
<script setup>
import { ref, inject } from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";

import Tag from 'primevue/tag';


import { i18n } from "@/i18n";
import { useRoute } from "vue-router";
const route = useRoute()
const { t: $t } = i18n.global;
const moment = inject("$moment")

const options = {
  fields: [
    { fieldname: "name", label: "Ref #", fieldtype: "Data" },
    { fieldname: "posting_date", label: "Posting Date" },
    { fieldname: "transaction_type", label: "Transaction Type" },
    { fieldname: "restriction_type", label: "Restriction Type" },
    { fieldname: "creation", fieldtype: "Datetime", label: "Creation" },
    
  ],
  filterOptions: [
  { fieldname: "posting_date" },  
  { fieldname: "transaction_type" },
  { fieldname: "restriction_type"}
    
  ],
    filters: [['property', '=', window.property_name],["rate_type","=",route.params.name],["transaction_type","in",["Prices update","Restriction update"]]],
};

function onViewLog(data){
    app.dialog.viewDataChangeLog(data.transaction_type, data.name)
    
}

 
</script>
