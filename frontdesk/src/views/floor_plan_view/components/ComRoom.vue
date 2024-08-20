<template>
  
    <!-- When edit mode show this template -->

 
      <template v-if="isRoomConflig">
        <div class="overflow-auto border-round-lg" style="background-color: red ; height: 100%" @contextmenu="onOpenMenu">

          <ComFloorPlanRoomConflict :room="room" :stay="stay" />
          <!-- render data from array -->
        </div>
      </template>
      <template v-else-if="stay">
        <template v-if="stay.type == 'Reservation'">
          <div class="overflow-auto border-round-lg box-shadow-floor-item item-floor-plan-room" @click="isMobile ? onClickMobile($event) : onViewReservationStay()" :style="{ backgroundColor:'#EEEEEE' , height: '100%' , borderTop: '6px solid',borderColor:stay.status_color }"
            @mouseenter="(event) => showTooltip(event)"  @contextmenu="onOpenMenu">
             
            <ComFloorPlanRoomReservation :room="room" :stay="stay" />
        <Dialog v-model:visible="showMenuOnMobile" modal :header="room?.room_type_alias + ' - ' + room?.room_number" :style="{ width: '25rem' }">
          <Menu :model="contextMenuItems" />  
        </Dialog>
          </div>
        </template>
        <ComFloorPlanRoomBlock v-else :roomBlock="roomBlock" :filters="filters" />


      </template>
      <template v-else-if="room.element">
        <div v-html="room.element" style="height: 100%;width:100%"></div>
      </template>

      <!-- vacant Room  -->
      <ComVacantRoom v-else :room="room" />


 


 

  <ContextMenu ref="menu" :model="contextMenuItems" />

</template>
<script setup>
import { getDoc, h, ref, useDialog, inject, postApi, computed } from "@/plugin"
import ComTooltip from "@/views/floor_plan_view/components/ComTooltip.vue"
const isMobile = ref(window.isMobile)
import ComUnblockRoom from "@/views/room_block/components/ComUnblockRoom.vue"
const showMenuOnMobile = ref(false);
import ComVacantRoom from "@/views/floor_plan_view/components/ComVacantRoom.vue"
import ComFloorPlanRoomReservation from "@/views/floor_plan_view/components/ComFloorPlanRoomReservation.vue"
import ComFloorPlanRoomConflict from "@/views/floor_plan_view/components/ComFloorPlanRoomConflict.vue"
import ComFloorPlanRoomBlock from "@/views/floor_plan_view/components/ComFloorPlanRoomBlock.vue"
import { useTippy } from "vue-tippy";
import ContextMenu from 'primevue/contextmenu';
import { i18n } from "@/i18n";
const moment = inject("$moment")

const { t: $t } = i18n.global;
const gv = inject("$gv")
const props = defineProps({
  room: Object,
  editMode: Boolean,
  filters: Object
})
const dialog = useDialog()
const menu = ref();
const contextMenuItems = ref([]);
const stay = computed(() => {
if (props.room.stay) {
    
    let s = props.room.stay.find(r => r.type == "Reservation" && (r.reservation_status || '') == 'In-house' && (r.is_departure || 0) == 1)
    
    if (!s) {
      s = props.room.stay.find(r => r.type == "Reservation" && r.reservation_status !='Checked Out')
    }
    
    if (!s) {
      s = props.room.stay.find(r => r.type == "Reservation")
    }
    if (!s) {
      s = props.room.stay.find(r => r.type == "Block")
    }
    return s
  }
  return
})


const arrivalStay = computed(() => {
  return props.room.stay.find(r => r.type == "Reservation" && (r.reservation_status || '') == 'Reserved' && (r.is_arrival || 0) == 1)
})


const roomBlock = computed(() => {
  return props.room.stay.find(r => r.type == "Block")
})
const stays = computed(() => {
  return props.room.stay.filter(r => r.type == "Reservation")
})

const isRoomConflig = computed(() => {
  if (props.room.stay) {
    return props.room.stay.filter(r => r.type == "Reservation" && (r.is_departure || 0) == 0).length > 1
  }
  return false
})


 
const onOpenMenu = (event) => {
  contextMenuItems.value = []
 
// add view stay 
if (stays.value.length == 1) {
  contextMenuItems.value.push({
    label: $t('View Reservation Stay Detail'), icon: 'pi pi-eye',
    command: function () {
      
      window.postMessage('view_reservation_stay_detail|' + stay.value.reservation_stay, '*')

    }
  })

  contextMenuItems.value.push(

    {
      label: $t('View Reservation Detail'), icon: 'pi pi-eye',
      command: function () {
        window.postMessage('view_reservation_detail|' + stay.value.reservation, '*')
      }
    }
  )


}else {
  // add sub menu to view to choose reservation stay or reservation
  contextMenuItems.value.push(
  {
    label: $t('View Reservation Stay'), icon: 'pi pi-copy',
    items:stays.value.map(r=>{
      return  {
        label: `${r.guest_name} (${r.reservation_stay})`  ,
        data:r,
        command:function(event){
          window.postMessage('view_reservation_stay_detail|' + event.item.data.reservation_stay, '*')
           
        }
      }
    })  
  }
)
}
//  check in
if (!isRoomConflig.value && stay.value && stay.value?.is_arrival && stay.value?.reservation_status=='Reserved') {
  contextMenuItems.value.push(
    {
      label: $t('Check In'), icon: 'pi pi-copy',
      command: function () {
          window.postMessage({action:"Check In from Floor Plan View",data:{reservation:stay.value.reservation, reservation_stay:[stay.value.reservation_stay]}})
      }
    }
  )

}
if(stay.value.reservation_status == 'In-house' ||  stay.value.reservation_status == 'Reserved'){

  contextMenuItems.value.push(
    {
      label: $t('Change Room'), icon: 'pi pi-copy',
      command: function () {
          alert("change room")

      }
    }
  )


}

  if (!window.isMobile) {
     menu.value.show(event);
  }
 
};

function onClickMobile(event){
  showMenuOnMobile.value = true
  onOpenMenu(event);
}

function onViewReservationStay() {

    window.postMessage('view_reservation_stay_detail|' + stay.value.reservation_stay, '*')

}

function onViewRoomBlock() {
  window.postMessage("view_room_block_detail|" + roomBlock.value.room_block_name,"*")
  
}

function showTooltip(event) {
  if(window.isMobile){
    return
  }
  if (!props.editMode) {
    useTippy(event.target, {
      content: h(ComTooltip, { data: props.room.stay}),
      interactive: true, 
      maxWidth: 'none',

    });
  }

  return;
}

</script>