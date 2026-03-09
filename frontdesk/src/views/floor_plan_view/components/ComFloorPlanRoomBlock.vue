<template>
<div  @click="onViewRoomBlock"  class="overflow-auto border-round-lg box-shadow-floor-item relative"  :style="{ backgroundColor:'#ffb5b4' , height: '100%' , borderTop: '6px solid',borderColor:roomBlock.status_color }"
            @mouseenter="(event) => showTooltip(event)" @contextmenu="onOpenMenu">
            <div class="flex absolute right-1 top-1 gap-2">
<div  v-tippy="{ content:'Room Block', placement: 'left' }" style="width:30px;height:30px;background-color: #fff;" class="flex justify-content-center align-content-center flex-wrap border-1 overflow-hidden border-round-lg box-shadow-floor-item">
       <ComIcon icon="RoomBlockIcon" height="16px" />
      </div>
      </div>          
            <div class="line-height-1 p-2">

  <div class="text-lg  font-medium">{{ roomBlock.room_id }}</div>
<div>Room Block</div>
<div class="mt-1">
    <i class="pi pi-calendar me-1"></i> {{ roomBlock.total_night_count }}
</div>
<hr class="my-2"> 
</div> 

           
          </div>
          <ContextMenu ref="menu" :model="contextMenuItems" />
</template>
<script setup>
import { getDoc, h, ref, useDialog, inject, postApi, computed } from "@/plugin"
import ComTooltip from "@/views/floor_plan_view/components/ComTooltip.vue"
import ComUnblockRoom from "@/views/room_block/components/ComUnblockRoom.vue"
import { useTippy } from "vue-tippy";
import ContextMenu from 'primevue/contextmenu';
import { i18n } from "@/i18n";
import ComIcon from "../../../components/ComIcon.vue";
const moment = inject("$moment")
const dialog = useDialog()
const contextMenuItems = ref([]);
const { t: $t } = i18n.global;
const gv = inject("$gv")
const menu = ref();
const props = defineProps({
    roomBlock: Object,
    filters:Object

})
function onViewRoomBlock() {
  window.postMessage("view_room_block_detail|" + props.roomBlock.room_block_name,"*")
  
}
function showTooltip(event) {
  if(window.isMobile){
    return
  }
  if (!props.editMode) {
    useTippy(event.target, {
      content: h(ComTooltip, { data:[props.roomBlock,props.filters] }),
      interactive: true, 
      maxWidth: 'none',

    });
  }

  return;
}
const onOpenMenu = (event) => {
    contextMenuItems.value = []
  contextMenuItems.value.push(
    {
      label: $t('View Room Block'), icon: 'pi pi-copy',
      command: function () {
       window.postMessage("view_room_block_detail|" + props.roomBlock.room_block_name,"*")
      }
    }
  )

  
  contextMenuItems.value.push(
    {
      label: $t('Unblock Room Block'), icon: 'pi pi-copy',
      command: function () {
        window.postMessage({action:"Unblock Room from Floor Plan View",data:{room_block_name:props.roomBlock.room_block_name,date:props.filters.date}},"*")
      }
    }
  )
  menu.value.show(event);
}
</script>