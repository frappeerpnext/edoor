<template>
  <ComDocumentList
    
    doctype="Channel Manager Sync Log"
    title="Channel Manager Sync Log"
    list_view_setting="channel_manager_sych_log_list"
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
      <template #status="{ item, index }">
   
        <Tag class="border-round" severity="success" v-if="item.status == 'Success'" :value="item.status" />
        <Tag class="border-round" severity="warning" v-else-if="item.status == 'Warning'" :value="item.status" />
        <Tag class="border-round" severity="error" v-else :value="item.status" />
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
    { fieldname: "provider", label: "CM. Provider" },
    { fieldname: "rate_type", label: "Rate Plan" },
    { fieldname: "request_type", label: "Request Type" },
    { fieldname: "status", label: "Status" },
    { fieldname: "response_text", label: "Reponse Text" },
    { fieldname: "sync_action", label: "Sync Action" },
    { fieldname: "creation", fieldtype: "Datetime", label: "Creation" },
    
  ],
  filterOptions: [
    { fieldname: "rate_type" },
    { fieldname: "request_type" },
    { fieldname: "status" },
    { fieldname: "posting_date" }
  ],
    filters: [['property', '=', window.property_name]],
};

function onViewLog(data){
    app.dialog.viewChannelManagerSyncLogData(data.title, data.name)
}

 
</script>
