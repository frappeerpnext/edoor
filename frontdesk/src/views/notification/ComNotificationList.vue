<template>
    <ComDialogContent @onOK="onSave"  hideButtonOK :loading="loading" hideButtonClose>
        <DataTable :value="data" tableStyle="min-width: 50rem">
            <Column header="Notification">
                <template #body="slotProps">
                    <div class="white-space-nowrap overflow-hidden text-overflow-ellipsis" style="width:700px">{{ slotProps.data.subject }}</div>
                </template>
            </Column>
            <Column field="document_type" header="Document"></Column>
            <Column field="document_name" header="Document #">
                <template #body="slotProps">
                            <Button @click="onViewDetail(slotProps.data)"  class="p-0 bg link_line_action w-auto bg-transparent px-1">
                                {{ slotProps.data.document_name }}
                              
                            </Button>
                            </template>

            </Column>
            <Column header="Reminded At">
                <template #body="slotProps">
                    <i><ComTimeago :date="slotProps.data.creation" /></i>
                </template>
            </Column>
    
        </DataTable>
        
        <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange"   :pageLinkSize="isMobile ? '2' : '5'">
                <template #start="slotProps">
                    <strong v-if="!isMobile">{{ $t('Total Records') }} : <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>

    </ComDialogContent>
</template>
<script setup>

import { onMounted } from 'vue';
import {ref,inject,getDocList,getCount} from "@/plugin"
import Paginator from 'primevue/paginator';
const dialogRef = inject('dialogRef');
const data = ref([])
const isMobile = ref(window.isMobile) 
const loading = ref(false)
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
function onViewDetail(d){
    window.postMessage(`view_${d.document_type.toLowerCase().replaceAll(" ","_")}_detail|${d.document_name}`,"*")
}
function getData(){
  loading.value = true
  getDocList("Notification Log",{
      fields:["*"],
      filters:[["for_user","=",window.user.name]],
      limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
      limit: pageState.value?.rows || 20,
      orderBy: {
          field: "modified",
          order: "DESC"
      },
  }).then(result=>{
      data.value = result
  }).finally(()=>{
    loading.value = false
  })

}

function getCountData(){

  getCount("Notification Log", 
   [["for_user","=",window.user.name]]
  ).then(result=>{
    pageState.value.totalRecords= result
     
  })
}
function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows
    getData()
}

onMounted(()=>{
    getData()
   getCountData()

    
})
</script>