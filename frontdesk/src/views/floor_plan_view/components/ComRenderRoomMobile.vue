<template>

   
  <template v-for="(d, index) in roomList.filter(r=>r.name && (r.is_deleted || 0)==0)" :key="index" >
    <ComRoom   :room="d" :editMode="editMode" :filters="filters"/>
  </template>
    
</template>
<script setup>
  import {ref} from  "@/plugin"
  import ComRoom from "@/views/floor_plan_view/components/ComRoom.vue";
 
  const props = defineProps({
    roomList:Object,
 
    filters:Object

  })
 
 
 
</script>

<style scoped>
.container {
  border: solid 1px red;
  width: 100%;
  height:100vh ;
  min-height: 768px;
  min-width: 1024px;
  max-width: 100%;
  background-image: var(--background-img);
  background-size: cover;
 

}
.edit .drv {
  border: dashed 1px #000;
}

.drv {
  border: solid 1px green;
}
</style>