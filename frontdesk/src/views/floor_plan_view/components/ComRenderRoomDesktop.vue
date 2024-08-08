<template>
  
<div :class="editMode == 1 ? ' edit' : ''">
      <draggable-resizable-container
        :grid="[20, 20]"
        :show-grid="editMode"
        class="container"
      >
        <template v-for="(d, index) in roomList" :key="index">
          <ComRoom :room="d" :editMode="editMode" :filters="filters"/>
        </template>
      </draggable-resizable-container>
    </div>
</template>
<script setup>
  import {ref} from  "@/plugin"
  import ComRoom from "@/views/floor_plan_view/components/ComRoom.vue";
  const props = defineProps({
    roomList:Object,
    editMode:Boolean,
    filters:Object

  })
</script>

<style scoped>
.container {
  border: solid 1px red;
  width: 100%;
  height: 85vh;
  min-height: 768px;
  min-width: 1024px;
  max-width: 100%;
}
.edit .drv {
  border: dashed 1px #000;
}

.drv {
  border: solid 1px green;
}
</style>