<template>
  <div> 
      <ComHeader isRefresh @onRefresh="loadData()">
          <template #start>
              <div class="text-2xl">Business Source Type</div>
          </template>me
          <template #end>
            <Button class="border-none" label="Add New Business Source Type" icon="pi pi-plus"  @click="onAddNewBusinessSourceType" />
          </template>
      </ComHeader>
      <div class="mb-3 w-20rem">
          <div class="flex w-full flex-wrap gap-2 ">
              <div class="p-input-icon-left w-full">
                  <i class="pi pi-search" />
                  <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
              </div>
          </div>
      </div>
      <div class="">
      <ComPlaceholder text="No Data" :loading="gv.loading"  :is-not-empty="gv.search(data, filter.keyword).length > 0">
      <!-- data?.filter((r)=>r.business_source_type.toLowerCase().includes((filter.keyword ||'').toLowerCase())) -->
      <DataTable  :value="gv.search(data, filter.keyword)" tableStyle="min-width: 50rem">
          <Column field="business_source_type" header="Business Source Type"></Column>
          <Column field="owner" header="Owner"></Column>
          <Column field="note" class="w-6" header="Note"></Column>
          <Column header="">
           <template #body="slotProps">
              <div class="flex gap-2 justify-end">
              <Button @click="onEdit(slotProps.data)" icon="pi pi-pencil text-sm" iconPos="right" class="h-2rem border-none" label="Edit" rounded />
              <Button @click="onDelete(slotProps.data.name)"  severity="danger"  icon="pi pi-trash text-sm" iconPos="right" class="h-2rem border-none" label="Delete" rounded />
              </div>
      </template>
      </Column>
      </DataTable>
      </ComPlaceholder>
      </div>
  </div>
</template>
<script setup>
import { inject, ref, getDocList, onMounted,useDialog,useConfirm,deleteDoc } from '@/plugin' 
import ComAddBusinessSourceType from "@/views/business_source/components/ComAddBusinessSourceType.vue"
const gv = inject("$gv")
const dialog = useDialog()
const data = ref([])
const filter = ref({})
const loading = ref(false)
const confirm = useConfirm()
function onDelete (name){
      confirm.require({
      message: 'Are you sure you want to delete business source type?',
      header: 'Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptClass: 'border-none crfm-dialog',
      rejectClass: 'hidden',
      acceptIcon: 'pi pi-check-circle',
      acceptLabel: 'Ok',
      accept: () => {
           deleteDoc('Business Source Type',name)
               .then(() =>{
                  loadData()
                  loading.value = false
               } ).catch((err)=>{
                  loading.value = false
               })         
      },
  });
}
function onEdit (edit){ 
dialog.open(ComAddBusinessSourceType, {
  props: {
      header: `Edit Business Source Type: ${edit.name}`,
      style: {
          width: '50vw',
      },
      breakpoints: {
          '960px': '75vw',
          '640px': '90vw'
      },
      modal: true,
      closeOnEscape: false,
      position: 'top'
  },
  data: edit,
  onClose:(options) => {
          const data = options.data;
          if(data){
      loadData()
    }
      }
});  
}
function loadData() {
  gv.loading = true
  getDocList('Business Source Type', {
      fields: ['business_source_type', 'note','owner','name'],
      limit: 10000,
  })
      .then((doc) => {
          data.value = doc
          gv.loading = false
      })
      .catch((error) => {
          gv.loading = false
       
      });
}
function onAddNewBusinessSourceType(){
  dialog.open(ComAddBusinessSourceType, {
      props: {
          header: `Add New Business Source Type`,
          style: {
              width: '50vw',
          },
          modal: true,
          closeOnEscape: false,
          position: 'top'
      },
      onClose:(options) => {
          const data = options.data;
          if(data){
      loadData()
    }
      }
  }); 
}
onMounted(() => {
  loadData()
})

</script>