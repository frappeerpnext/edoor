<template>
  <div :class="editMode == 1 ? 'edit' : 'floor-plan-item'">

<template v-if="editMode">
<draggable-resizable-container
:grid="editMode?[10, 10]:[0,0]"
:show-grid="editMode"
class="container"

@contextmenu="onOpenMenu"   
>

  <draggable-resizable-vue v-for="(room, index) in roomList.filter(r=>(r.is_deleted || 0)==0)" :key="index"
    v-model:x="room.x" v-model:y="room.y" v-model:h="room.height"
  v-model:w="room.width" v-model:active="room.isActive" :draggable="editMode" :resizable="editMode" :z="room.z_index"
   :min-width="room.element?10:10"
   :min-height="room.element?20:20"
  >   
  <ComRoomArrangeLayout   :room="room"  />
  </draggable-resizable-vue>


</draggable-resizable-container>
</template>
<template v-else>
<div class="container">
 
  <div v-for="(room, index) in roomList.filter(r=>(r.is_deleted || 0)==0)" :key="index"
  :class="room.element?'':'drv'"
  :style="{position:'absolute',left:room.x+'px',top:room.y+'px',height:room.height+ 'px',width:room.width+'px',zIndex:room.z_index}"
  >   
    <div v-if="room.element == 'Floor Info' ">
 
<div class="grid font-bold border-bottom-1 surface-border">
  <div class="col text-center p-1">Room Type</div>
  <div class="col text-center p-1">Total Rooms</div>
  <div class="col text-center p-1">Availability</div>
</div>

<!-- Rows -->
<div 
  class="grid border-bottom-1 surface-border" 
  v-for="roomType in [...new Set(roomList.filter(r => r.room_type).map(r => r.room_type))]" 
  :key="roomType"
>
  <!-- Room Type -->
  <div class="col text-center p-1">
    {{ roomType }}
  </div>

  <!-- Total Rooms -->
  <div class="col text-center p-1">
    {{ roomList.filter(r => r.room_type === roomType).length }}
  </div>

  <!-- Availability -->
  <div class="col text-center p-1">
    {{ roomList.filter(r => r.room_type === roomType && (!r.stay || r.stay.length === 0)).length }}
  </div>
</div>
<div class="grid font-bold">
  <div class="col-4 text-center p-1">Total</div>
  <div class="col-4 text-center p-1">
    {{ roomList.filter(r => r.room_type ).length }}
  </div>
  <div class="col-4 text-center p-1">
   {{ roomList.filter(r => r.room_type && (!r.stay || r.stay.length === 0)).length }}
  </div>
  <div class="col-6 text-center p-1">
    Arrival
  </div>
  <div class="col-6 text-center p-1">
    {{ roomList.reduce((sum, r) => sum + (r.stay?.filter(s => s.is_arrival === 1).length || 0), 0) }}
  </div>
   <div class="col-6 text-center p-1">
    Stay Over
  </div>
  <div class="col-6 text-center p-1">
    {{ roomList.reduce((sum, r) => sum + (r.stay?.filter(s => s.is_stay_over === 1).length || 0), 0) }}
  </div>
   <div class="col-6 text-center p-1">
   Departure
  </div>
  <div class="col-6 text-center p-1">
     {{ roomList.reduce((sum, r) => sum + (r.stay?.filter(s => s.is_departure === 1).length || 0), 0) }}
  </div>
</div>

    </div>
    <ComRoom   :room="room" :editMode="editMode" :filters="filters"/>
</div>


</div>
</template>


</div>


<ContextMenu ref="menu" :model="contextMenuItems" />
   
</template>
<script setup>
import {ref} from  "@/plugin"
import ComRoom from "@/views/floor_plan_view/components/ComRoom.vue";
import DraggableResizableVue from "draggable-resizable-vue3";
import ComRoomArrangeLayout from "@/views/floor_plan_view/components/ComRoomArrangeLayout.vue"
import ContextMenu from 'primevue/contextmenu';
import { onUnmounted } from "vue";

const emit = defineEmits(["onAddElement"])

const props = defineProps({
  roomList:Object,
  editMode:Boolean,
  filters:Object

})
const menu = ref();
const contextMenuItems = ref([
    { label: 'Add Element', icon: 'pi pi-copy',
      command:function(event){
  
        emit("onAddElement")
      }
     },
    {
      label:"Set Container Height",
      command:function(){
        
      }
    }
]);

const onOpenMenu = (event) => {
  if(props.editMode){
    menu.value.show(event);
  }
  
};
 



</script>

<style scoped>
.container {
border: none;
width: 100%;
 height: var(--container-height);
min-height: 768px;
min-width: 1024px;
max-width: 100%;
background-image: var(--background-img);
background-size: cover;
border-radius: 10px;
position:relative;


}
.edit .container{border:  1px solid #000;border-radius: 0px;}
.edit .drv {
border: dashed 1px #0056ff;
--d04bd352-handlesBorder:0.5px solid #0056ff !important

}

.drv {
border: none
}
.custom-table  tr  td {
  border: none !important;
  background: none !important;
}
</style>