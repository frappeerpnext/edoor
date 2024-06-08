<template>
    <div class="w-5 m-auto mt-3">
        <div class="flex gap-2 mb-2">
            <BlockUI class="w-full" :blocked="loading">
    <ComSelect  class="w-full" doctype="Account Code" v-model="parent_account_code" optionLabel="account_name" optionValue="name" :filters="[['parent_account_code','=','All Account Code']]" />
    </BlockUI>
    <Button :class="!parent_account_code ? 'pointer-events-none opacity-60':''" :loading="loading" label="Save" icon="pi pi-save" class="w-6rem" @click="getSortOrderList" />
</div>
<div></div>
<div class="flex justify-center mt-4" v-if="!parent_account_code">
   
            <span class="text-md ms-4">
            Please Select Account Code 
            </span>
        </div>
<ComReservationStayPanel :blockUI="loading" v-if="data.length>0 && parent_account_code" class="bg-white" title="Sort Main Account Code">
    <template #content>
<div    v-sortable="false"> 
    <div    :data-name="a.name"  v-for="(a, index) in data.filter(r=>r.parent_account_code==parent_account_code)" :key="index" class="account_code w-full border-1 border-dark border-700 py-2 px-3 bg-gray-100 mt-2 border-round-lg cursor-move">
        <span> <i class="pi pi-arrows-alt me-3"></i> </span> {{ a.account_name }} - {{ a.name }}
    </div>

</div>
</template>
</ComReservationStayPanel>
<hr class="my-3">
<ComReservationStayPanel :blockUI="loading" v-if="parent_account_code"  class="bg-white mb-4" title="Sort Sub Account Code">
<template #content>
 <template    v-for="(p, index) in data.filter(r=>r.parent_account_code==parent_account_code)" :key="index">
    <ComReservationStayPanel class="mb-2 " :title="p.account_name">
        <template #content>
<div  v-sortable> 
    <div  :data-name="a.name" :data-parent="p.name"  v-for="(a, index) in data.filter(r=>r.parent_account_code==p.name)" :key="index" class="py-2 px-3 child_account_code w-full border-1 border-dark border-700 bg-gray-100 mt-2 border-round-lg cursor-move">
       <div>
        <span> <i class="pi pi-arrows-alt me-3"></i> </span> {{ a.account_name }}  {{ a.name }}
       </div>
    </div>
</div>
        </template>
    </ComReservationStayPanel>
    
    
 </template>
</template>
</ComReservationStayPanel>
</div>
  </template>
  <script setup>
  import {getDocList,ref,onMounted,postApi} from "@/plugin"
  import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
  import BlockUI from 'primevue/blockui';
  const loading = ref(false)
  const parent_account_code = ref("")
 
 
  const data =ref([])

  function onOrderChange(event){
    
    
  }

 

  function getSortOrderList(){
    loading.value = true
 
        let elments = document.querySelectorAll(".account_code")
        let parentAccountCode = []
        elments.forEach((el)=>{
            parentAccountCode.push(el.dataset.name)
        })

        postApi("utils.sort_parent_account_code", {
            parent_account_code:parent_account_code.value,
            account_codes:parentAccountCode
        }).then(r=>{
            loading.value = false
            elments = document.querySelectorAll(".child_account_code")
            let accountCodes = []
            elments.forEach((el)=>{
                accountCodes.push({account_code:el.dataset.name, parent:el.dataset.parent})
            })
            
            postApi("utils.sort_child_account_code", {
                account_codes:accountCodes
            })
        })
  }

  onMounted(()=>{
    getDocList("Account Code",{
        fields:["name","parent_account_code","account_name","sort_order"],
        filters:[["parent_account_code","!=","All Account Code"]],
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
