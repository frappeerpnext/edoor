<template>
    <div class="w-5 m-auto mb-5 mt-3">
    <ComReservationStayPanel :blockUI="loading" v-if="data.length>0" class="bg-white" title="Account Category Sort Order">
    <template #btn>
        <!-- <Button class="border-none" @click="onSave">Save</Button> -->
        <Button :loading="loading" label="Save" icon="pi pi-save" class="w-6rem" @click="onSave" />
    </template>
    <template #content>
        <BlockUI class="w-full" :blocked="loading">
   <div v-if="data.length>0"  v-sortable> 
    <div  :data-name="a.name"  v-for="(a, index) in data" :key="index" class=" flex align-items-center w-full border-1 border-dark border-700 py-2 px-3 bg-gray-100 mt-2 border-round-lg cursor-move">
        <span class="flex"> <i class="pi pi-arrows-alt me-3"></i> </span>
        <span class="flex align-items-center">{{ a.name }} </span>
        
    </div>

</div> </BlockUI>    
    </template>

</ComReservationStayPanel>
</div>
 </template>

  <script setup>
  import {getDocList,ref,onMounted,postApi} from "@/plugin"
  import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
  const parent_account_code = ref("")
  const loading = ref(false)
 
  const data =ref([])

  

 

  function onSave(){
    loading.value = true
        let elments = document.querySelectorAll(".account_category")
        let account_categories = []
        elments.forEach((el)=>{
            account_categories.push(el.dataset.name)
        })

        postApi("utils.sort_account_categories", {
            account_categories:account_categories
        }).then(r=>{
            loading.value = false
             
        })


  }

  onMounted(()=>{
    getDocList("Account Category",{
        fields:["name","sort_order"],
        limit: 1000    ,
        orderBy: {
            field: 'sort_order'
        },
    }
        ).then(result=>{
        data.value = result
    })
  })

  
</script>
