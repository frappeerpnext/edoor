<template>
  <draggable-resizable-vue :key="index" v-model:x="room.x" v-model:y="room.y" v-model:h="room.height"
    v-model:w="room.width" v-model:active="room.isActive" :draggable="editMode" :resizable="editMode">

    <template v-if="room.stay && !editMode">
      <div @click="onViewReservationStay"
        :style="{ background: editMode ? '' : room.stay.status_color, height: '100%' }"
        @mouseover="(event) => showTooltip(event)" @contextmenu="onOpenMenu">
        {{ room.name }} <br>
        {{ room.room_number }} <br>
        {{ room.stay.guest_name }}
        {{ room.stay.arrival_date }}
        {{ room.stay.departure_date }}
        {{ room.stay.adult }}
        {{ room.stay.child }}
        {{ room.stay.reservation_status }}
        is_arrival:{{ room.stay.is_arrival }}


      </div>
    </template>
    <template v-else>
      <div @contextmenu="onOpenMenu" style="height: 100%;">
       
        {{ room.room_number }}

      </div>

    </template>


  </draggable-resizable-vue>
  <ContextMenu ref="menu" :model="contextMenuItems" />

</template>
<script setup>
import { h, ref, useDialog,inject,postApi  } from "@/plugin"
import ComTooltip from "@/views/floor_plan_view/components/ComTooltip.vue"
import ComConfirmCheckIn from "@/views/reservation/components/confirm/ComConfirmCheckIn.vue"
import NewReservation  from "@/views/reservation/NewReservation.vue"

import DraggableResizableVue from "draggable-resizable-vue3";
import { useTippy } from "vue-tippy";
import ContextMenu from 'primevue/contextmenu';
import { i18n } from "@/i18n";
const moment = inject("$moment")

const { t: $t } = i18n.global;
const gv = inject("$gv")
const props = defineProps({
  room: Object,
  editMode: Boolean,
  filters:Object
})
const dialog = useDialog()
const menu = ref();
const contextMenuItems = ref([]);

// add view stay 
if (props.room.stay) {
  contextMenuItems.value.push({
    label: $t('View Reservation Stay Detail'), icon: 'pi pi-copy',
    command: function () {
      window.postMessage('view_reservation_stay_detail|' + props.room.stay.reservation_stay, '*')
    }
  })

  contextMenuItems.value.push(

    {
      label: $t('View Reservation Detail'), icon: 'pi pi-copy',
      command: function () {
        window.postMessage('view_reservation_detail|' + props.room.stay.reservation, '*')
      }
    }
  )

  if (props.room.stay.is_arrival) {
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
                gv.loading= true

                postApi("reservation.check_in", {
                  reservation: props.room.stay.reservation,
                  reservation_stays: [props.room.stay.reservation_stay],
                  note: result.note,
                  arrival_time: result.checked_in_date
                }).then((result) => {
                  gv.loading= false
                  window.postMessage({ action: "FloorPlanView" }, "*")
                })
                  .catch((err) => {
                    gv.loading= false
                  })
              }
            }
          })

        }
      }
    )

  }

}
// add block room
if (!props.room.stay) {
  contextMenuItems.value.push({
    label: $t('Add New FIT Reservation'), icon: 'pi pi-copy',
    command: function () {
     
      dialog.open(NewReservation, {
            data: {
                arrival_date: moment(props.filters.date).toDate(),
                departure_date:  moment(props.filters.date).add(1, "days").toDate(),
                room_type_id: props.room.room_type_id,
                room_id: props.room.name
            },
            props: {
                header: $t('New Reservation'),
                style: {
                    width: '80vw',
                },
                breakpoints: {
                    '960px': '100vw',
                    '640px': '100vw'
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: 'top',

            },
            onClose: (options) => {
                const data = options.data;
                if (data != undefined) {
                  window.postMessage('view_reservation_stay_detail|' + data.name, '*')
                }
            }
        });
    }
  })


  contextMenuItems.value.push({
    label: $t('Block this Room'), icon: 'pi pi-copy',
    command: function () {
      alert("add room block")
    }
  })
}

const onOpenMenu = (event) => {
  menu.value.show(event);
};


function onViewReservationStay() {
  if (!props.editMode) {
    window.postMessage('view_reservation_stay_detail|' + props.room.stay.reservation_stay, '*')
  }

}

function showTooltip(event) {
  if (!props.editMode) {
    useTippy(event.target, {
      content: h(ComTooltip, { data: props.room.stay }),
      placement: "top",
     
      interactive:true

    });
  }

  return;
}

</script>