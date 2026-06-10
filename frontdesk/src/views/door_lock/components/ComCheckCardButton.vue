<template>
    <Button severity="warning" label="Check Card" @click="onCheckCard"></Button>
</template>
<script setup>

 import  ComShowCardInfo from "@/views/door_lock/components/ComShowCardInfo.vue"

async function onCheckCard(){
    const l = await window.showLoading("Checking card info...");
 
    const res = await app.getApi(
      "edoor.integration.door_lock.china.integration.read_card",
      {
        property: window.property_name
      }
    )
    l.close();
    if (res.data){
      
       app.utils.openDialog(ComShowCardInfo,"Card Information",{data:res.data});


    }

  

}

</script>