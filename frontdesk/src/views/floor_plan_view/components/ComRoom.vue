<template>
  
    <!-- When edit mode show this template -->
    <ComRoomArrangeLayout v-if="editMode" :room="room"  />
    <template v-else>
      <template v-if="isRoomConflig">
        <div class="overflow-auto border-round-lg" style="background-color: red ; height: 100%" @contextmenu="onOpenMenu">

          <ComFloorPlanRoomConflict :room="room" :stay="stay" />
          <!-- render data from array -->
        </div>
      </template>
      <template v-else-if="stay">
        <template v-if="stay.type == 'Reservation'">
          <div class="overflow-auto border-round-lg box-shadow-floor-item" @click="onViewReservationStay" :style="{ backgroundColor:'#EEEEEE' , height: '100%' , borderTop: '10px solid',borderColor:stay.status_color }"
            @mouseenter="(event) => showTooltip(event)" @contextmenu="onOpenMenu">
             
            <ComFloorPlanRoomReservation :room="room" :stay="stay" />
          </div>
        </template>

        <template v-else>
          <div @click="onViewRoomBlock" :style="{ background: stay.status_color, height: '100%' }"
            @mouseenter="(event) => showTooltip(event)" @contextmenu="onOpenMenu">
         
          {{ roomBlock }}
           
          </div>
        </template>

      </template>
      <template v-else-if="room.element">
        <div v-html="room.element" style="height: 100%;width:100%"></div>
      </template>

      <!-- vacant Room  -->
      <ComVacantRoom v-else :room="room" />


    </template>


 

  <ContextMenu ref="menu" :model="contextMenuItems" />

</template>
<script setup>
import { getDoc, h, ref, useDialog, inject, postApi, computed } from "@/plugin"
import ComTooltip from "@/views/floor_plan_view/components/ComTooltip.vue"
import ComConfirmCheckIn from "@/views/reservation/components/confirm/ComConfirmCheckIn.vue"
import ComUnblockRoom from "@/views/room_block/components/ComUnblockRoom.vue"


import ComVacantRoom from "@/views/floor_plan_view/components/ComVacantRoom.vue"
import ComFloorPlanRoomReservation from "@/views/floor_plan_view/components/ComFloorPlanRoomReservation.vue"
import ComFloorPlanRoomConflict from "@/views/floor_plan_view/components/ComFloorPlanRoomConflict.vue"
import ComRoomArrangeLayout from "@/views/floor_plan_view/components/ComRoomArrangeLayout.vue"

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
    label: $t('View Reservation Stay Detail'), icon: 'pi pi-copy',
    command: function () {
      alert('view_reservation_stay_detail|' + stay.value.reservation_stay)
      window.postMessage('view_reservation_stay_detail|' + stay.value.reservation_stay, '*')
    }
  })

  contextMenuItems.value.push(

    {
      label: $t('View Reservation Detail'), icon: 'pi pi-copy',
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

        dialog.open(ComConfirmCheckIn, {
          props: {
            header: $t('Confirm Check In'),
            style: {
              width: '650px',
            },
            modal: true,
            closeOnEscape: false,
            breakpoints: {
              '960px': '650px',
              '640px': '100vw'
            },

          },
          onClose: (options) => {
            const result = options.data;
            if (result) {
              gv.loading = true
              postApi("reservation.check_in", {
                reservation: props.room.stay.reservation,
                reservation_stays: [props.room.stay.reservation_stay],
                note: result.note,
                arrival_time: result.checked_in_date
              }).then((result) => {
                gv.loading = false
                window.postMessage({ action: "FloorPlanView" }, "*")
              })
                .catch((err) => {
                  gv.loading = false
                })
            }
          }
        })

      }
    }
  )

}

// add view room block menu
if (roomBlock.value) {
  if(stay.value){
    contextMenuItems.value.push( {
        separator: true
    })
  }
  contextMenuItems.value.push(
    {
      label: $t('View Room Block'), icon: 'pi pi-copy',
      command: function () {
       window.postMessage("view_room_block_detail|" + roomBlock.value.room_block_name,"*")
      }
    }
  )

  
  contextMenuItems.value.push(
    {
      label: $t('Unblock Room Block'), icon: 'pi pi-copy',
      command: function () {
       
     if(window.isMobile){
          const elem = document.querySelector(".p-dialog");
          elem?.classList.add("p-dialog-maximized"); // adds the maximized class

      }
      getDoc("Room Block",roomBlock.value.room_block_name).then(doc=>{
        doc.unblock_date = moment(props.filters.date).toDate()
          doc.unblock_housekeeping_status_code =window.setting.housekeeping_status_code[0].status
          dialog.open(ComUnblockRoom, {
              data: doc,
              props: {
                  header: $t('Unblock Room') + "-" + doc.name,
                  style: {
                      width: '50vw',
                  },
                  modal: true,
                  position: 'top',
                  closeOnEscape: false,
                  breakpoints:{
                      '960px': '50vw',
                      '640px': '100vw'
                  },
              },
              onClose: (options) => {
                  window.postMessage({action:"FloorPlanView"},"*")
              }
          })
      })
      
      }
    }
  )




}


  menu.value.show(event);
};


function onViewReservationStay() {
  if (stay.value && stay.value.type=="Reservation") {
      window.postMessage('view_reservation_stay_detail|' + stay.value.reservation_stay, '*')
  }

}

function onViewRoomBlock() {
  
  window.postMessage("view_room_block_detail|" + roomBlock.value.room_block_name,"*")
  
}
function oncheckin(){
  alert (3434)
}
function showTooltip(event) {
  if(window.isMobile){
    return
  }
  if (!props.editMode) {
    useTippy(event.target, {
      content: h(ComTooltip, { data: props.room.stay , checkin:oncheckin  }),
      interactive: true, 
      maxWidth: 'none',

    });
  }

  return;
}

</script>