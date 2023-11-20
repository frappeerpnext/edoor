<template>
    <h1>My Component</h1>
    <ComSelect doctype="Account Code" v-model="parent_account_code" optionLabel="account_name" optionValue="name" :filters="[['parent_account_code','=','All Account Code']]" />
    <Button @click="getSortOrderList">Save</Button>
<div v-if="data.length>0 && parent_account_code"   v-sortable @end="onOrderChange"> 
    <div    :data-name="a.name"  v-for="(a, index) in data.filter(r=>r.parent_account_code==parent_account_code)" :key="index" class="account_code pa-4 bg-green-200 mt-2">
        {{ a.account_name }} {{ a.name }}
       
    </div>

</div>
<h1>sort sub accoun t</h1>
 <template v-if="parent_account_code"   v-for="(p, index) in data.filter(r=>r.parent_account_code==parent_account_code)" :key="index">
 <h1>{{p.account_name}}</h1>
    <div  v-sortable> 
    <div  :data-name="a.name" :data-parent="p.name"  v-for="(a, index) in data.filter(r=>r.parent_account_code==p.name)" :key="index" class="child_account_code pa-4 bg-green-200 mt-2">
       <div style="padding: 10px;">
        {{ a.account_name }} {{ a.name }}
       </div>
        

    </div>

</div>
 </template>
 

    
  </template>
  <script setup>
  import {getDocList,ref,onMounted,postApi} from "@/plugin"
  const parent_account_code = ref("")
 
 
  const data =ref([])

  function onOrderChange(event){
    
    
  }

 

  function getSortOrderList(){
        let elments = document.querySelectorAll(".account_code")
        let parentAccountCode = []
        elments.forEach((el)=>{
            parentAccountCode.push(el.dataset.name)
        })

        postApi("utils.sort_parent_account_code", {
            parent_account_code:parent_account_code.value,
            account_codes:parentAccountCode
        }).then(r=>{
            
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
