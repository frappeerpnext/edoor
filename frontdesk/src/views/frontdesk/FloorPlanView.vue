<template>
hello
<DataTable :value="data" tableStyle="min-width: 50rem">
    <Column field="name" header="Name"></Column>
    <Column field="room_number" header="room #"></Column>
    <Column field="room type" header="room type"></Column>
    
</DataTable>

</template>
<script setup>
  import {ref,getApi,onMounted} from "@/plugin"
  const data = ref([])
  onMounted(()=>{
    getApi("test.get_data").then(r=>{
      data.value = r.message
    })
  })
</script>