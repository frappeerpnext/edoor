<template>
  <ComFrontDeskLayout :showSetting="true">
    <template #setting_menu>
      <button   @click="onEnableArrangeFloorPlan" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                     <i class="pi pi-cog me-2" ></i>
                      {{ $t('Arrange Floor Plan') }}
     </button>
    </template>
<Button @click="onSavePosition">Save Setting {{ editMode }}</Button>
<div :class="editMode==1?' edit':''">
<draggable-resizable-container
  :grid="[20, 20]"
  :show-grid="editMode"
  class="container"
>
  <draggable-resizable-vue
    v-for="(d, index) in room_list" :key="index"
    v-model:x="d.x"
    v-model:y="d.y"
    v-model:h="d.height"
    v-model:w="d.width"
    v-model:active="d.isActive"
    :draggable="editMode"
    :resizable="editMode"
  >

    {{ d.room_number }}

  </draggable-resizable-vue>

</draggable-resizable-container>
</div>
</ComFrontDeskLayout>
</template>

<script setup>
import { ref,getApi,onMounted,postApi } from '@/plugin'
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import DraggableResizableVue from 'draggable-resizable-vue3'


const room_list = ref([])
const editMode = ref(false)
function onEnableArrangeFloorPlan(){
editMode.value =!editMode.value
}
function getRoom(){
getApi("frontdesk.get_room_for_floor_plan_arrangement",{
  filters:{
    property:window.property_name,
    floor:"Ground Floor"
  }
}).then(r=>{
  room_list.value = r.message
})
}


function onSavePosition(){
postApi("frontdesk.save_room_layout_position",{
  floor:"Ground Floor",
  data: room_list.value.map((r)=>{
    return {
      name:r.name,
      x:r.x,
      y:r.y,
      width:r.width,
      height:r.height
    }
  })
}).then(r=>{
  editMode.value = false
})
}
onMounted(()=>{
getRoom();

})
</script>


<style scoped>

.container {
border:solid 1px red;
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