<template>
    <h1>Account Category Sort Order</h1>
    
    <Button @click="onSave">Save</Button>

<div v-if="data.length>0"  v-sortable> 
    <div  :data-name="a.name"  v-for="(a, index) in data" :key="index" class="account_category pa-4 bg-green-200 mt-2">
        {{ a.name }} 
    </div>

</div>
 </template>

  <script setup>
  import {getDocList,ref,onMounted,postApi} from "@/plugin"
  const parent_account_code = ref("")
 
 
  const data =ref([])

  

 

  function onSave(){
        let elments = document.querySelectorAll(".account_category")
        let account_categories = []
        elments.forEach((el)=>{
            account_categories.push(el.dataset.name)
        })

        postApi("utils.sort_account_categories", {
            account_categories:account_categories
        }).then(r=>{
            
             
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
