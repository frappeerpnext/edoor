<template>
     <ComDialogContent hideButtonOK @onClose="onClose" style="max-height: 70vh;" :loading="loading">
  <div >
    <!-- Summary -->
    <div class="grid mb-4">
      <div class="col-12 md:col-4">
        <div class="surface-card shadow-2 border-round p-4">
          <div class="flex justify-content-between">
            <div>
              <span class="block text-500 mb-2">Pending</span>
              <span class="text-3xl font-bold text-orange-500">{{ ClosedCount }}</span>
            </div>
            <i class="pi pi-clock text-orange-400 text-4xl"></i>
          </div>
        </div>
      </div>

      <div class="col-12 md:col-4">
        <div class="surface-card shadow-2 border-round p-4">
          <div class="flex justify-content-between">
            <div>
              <span class="block text-500 mb-2">Completed</span>
              <span class="text-3xl font-bold text-green-500">{{ openCount }}</span>
            </div>
            <i class="pi pi-check-circle text-green-400 text-4xl"></i>
          </div>
        </div>
      </div>

      <div class="col-12 md:col-4">
        <div class="surface-card shadow-2 border-round p-4">
          <div class="flex justify-content-between">
            <div>
              <span class="block text-500 mb-2">Cancelled</span>
              <span class="text-3xl font-bold text-red-500">{{ cancelledCount }}</span>
            </div>
            <i class="pi pi-times-circle text-red-400 text-4xl"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="p-2">
   <ComDocumentList
    
    doctype="ToDo"
    title="ToDo"
    list_view_setting="channel_manager_todo_list"
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
        <template #priority="{ item, index }">
            <span class="p-3" :class="getPriorityClass(item.priority)">
        {{ item.priority }}
    </span>
        </template>
  </ComDocumentList>
  </div>
  
  </ComDialogContent>
</template>

<script setup>
import { ref, inject , getDialogScrollHeight,onMounted} from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";

import Tag from 'primevue/tag';
const getPriorityClass = (priority) => {
    const base = "px-2 py-1 text-xs font-semibold rounded-full ";
    
    if (priority === 'High') return base + 'bg-red-100 text-red-800';
    if (priority === 'Medium') return base + 'bg-yellow-100 text-yellow-800';
    return base + 'bg-green-100 text-green-800'; // Low or default
};

import { i18n } from "@/i18n";
import { useRoute } from "vue-router";
const route = useRoute()
const { t: $t } = i18n.global;
const moment = inject("$moment")
const scrollHeight = ref("400px");
const cmTaskData = ref()
const openCount = ref(0)
const cancelledCount = ref(0)
const ClosedCount = ref(0)
const options = {
  fields: [
    { fieldname: "name", label: "Task ID", fieldtype: "Data" },

    { 
      fieldname: "custom_subject", 
      label: "Subject", 
      fieldtype: "Data" 
    },
   

    { 
      fieldname: "reference_type", 
      label: "Reference Type", 
      fieldtype: "Data" 
    },

    { 
      fieldname: "date", 
      label: "Date", 
      fieldtype: "Date" 
    },

    { 
      fieldname: "creation", 
      label: "Created On", 
      fieldtype: "Datetime" 
    },
      { 
      fieldname: "status", 
      label: "Status", 
      fieldtype: "Data" 
    },
     { 
      fieldname: "priority", 
      label: "Priority", 
      fieldtype: "Data" 
    },
  ],

  filters: [
    ['custom_property', '=', window.property_name]
  ],

  filterOptions: [
    { fieldname: "status" },
    { fieldname: "priority" },
    { fieldname: "owner" },
    { fieldname: "custom_property" },
    { fieldname: "creation" }
  ],

  hideSaveView: false,

  scrollHeight: 'calc(70vh - 400px)'
};
async function getCMTaskData() {
    const res = await app.getDocList("ToDo", {
        fields: ["name", "status", "priority", "custom_subject", "description","modified"],
        filters: [["custom_property", "=", window.property_name]],
        orderBy: {
            field: 'modified',
            order: 'desc',
        }
    })
    if (res.data) {
        cmTaskData.value = res.data
        openCount.value = res.data.filter(d => d.status == "Open").length
        cancelledCount.value = res.data.filter(d => d.status == "Cancelled").length
        ClosedCount.value = res.data.filter(d => d.status == "Closed").length
    }
}
onMounted(() => {
    getCMTaskData()
  scrollHeight.value = getDialogScrollHeight(0);
});
function onViewLog(data){
    app.dialog.viewChannelManagerSyncLogData(data.request_type, data.name)
}

</script>

<style scoped>
.task-scroll {
  max-height: 70vh;
  overflow-y: auto;
}

.task-item {
  transition: all 0.2s ease;
  background: var(--surface-card);
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.task-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  font-size: 1.2rem;
  color: white;
}

.task-icon.Pending {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.task-icon.Completed {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.task-icon.Failed {
  background: linear-gradient(135deg, #ef4444, #f87171);
}
</style>