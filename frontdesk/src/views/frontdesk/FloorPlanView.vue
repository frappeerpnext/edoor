<template>
  <ComFrontDeskLayout :title="$t('Map View')">
<DataTable :value="data" tableStyle="min-width: 50rem">
    <Column field="name" header="Name"></Column>
    <Column field="room_number" header="room #"></Column>
    <Column field="room type" header="room type"></Column>
    
</DataTable>
</ComFrontDeskLayout>
</template>
<script setup>
  import {ref,getApi,getDocList,onMounted} from "@/plugin"
  import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
  import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
  const data = ref([])
  onMounted(()=>{
    getDocList("Room",
    {
      fields:["name","room_number","room_type"],
      limit:5
    }

    ).then(r=>{
      data.value = r
    })
  })
</script>