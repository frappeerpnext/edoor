<template>
  <ComDialogContent hideButtonOK @onClose="onClose" style="max-height: 70vh;" :loading="loading">
  <ComDocumentList
    
    doctype="Channel Manager Sync Log"
    title="Channel Manager Sync Log"
    list_view_setting="channel_manager_sych_log_list_dialog"
    :options="options"
    wrap-class="surface-50 "
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
      <template #response_text="{ item, index }">
     <div v-tippy="item.response_text" class="white-space-nowrap overflow-hidden text-overflow-ellipsis" style="max-width: 250px;">
    {{ item.response_text }}
  </div>
          </template>
     
  </ComDocumentList>
  </ComDialogContent>
</template>
<script setup>
import { ref, inject , getDialogScrollHeight,onMounted} from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";

import Tag from 'primevue/tag';


import { i18n } from "@/i18n";
import { useRoute } from "vue-router";
const route = useRoute()
const { t: $t } = i18n.global;
const moment = inject("$moment")
const scrollHeight = ref("400px");
const dialogRef = inject("dialogRef");

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
      hideSaveView: false,
  scrollHeight: 'calc(70vh - 200px)'
};

onMounted(() => {
  scrollHeight.value = getDialogScrollHeight(0);
});
function onViewLog(data){
    app.dialog.viewChannelManagerSyncLogData(data.request_type, data.name)
}

const onClose = () => { 
    dialogRef.value.close(true)
}

</script>
