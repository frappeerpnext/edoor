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
   :min-width="room.element?50:180"
   :min-height="room.element?50:120"
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
        alert(123)
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
height:100vh ;
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
</style>