<template>
  <div class="border-round-lg p-2 overflow-hidden box-shadow-floor-item" @contextmenu="onOpenMenu" style="height: 100%;background-color: white;min-height: 100px;min-width:150px;">
<div class="line-height-1">
  <div class="text-lg  font-medium">{{ room?.room_type_alias }} - {{ room.room_number }}</div>
<div class="w-full text-overflow-ellipsis">
  Vacant Room
</div>
<div>
  <div class="mt-auto">
  <hr class="my-2">
        </div>
        <div class="flex gap-2">
            <ComChipIcon v-tippy="{ content: room?.housekeeping_status_code, placement: 'left' }" svgIcon="broom" iconHeight="12px" :bgColor="room?.status_color" /> 
        </div>
</div>
</div> 
      
   

    <!-- {{ pageData }} -->
  </div>
  <ContextMenu ref="menu" :model="contextMenuItems" />
</template>
<script setup>
import { ref, inject, useDialog } from "@/plugin"
import { i18n } from "@/i18n";
import ComEditRoomBlock from "@/views/room_block/components/ComEditRoomBlock.vue";
import ComAssignReservationStayToRoom from "@/views/floor_plan_view/components/ComAssignReservationStayToRoom.vue";
import ContextMenu from 'primevue/contextmenu';
import { useTippy } from "vue-tippy";
import ComChipIcon from '@/views/floor_plan_view/components/ComChipIcon.vue'
const pageData = inject('pageData')
const menu = ref()
const dialog = useDialog()
const contextMenuItems = ref([])
const gv = inject("$gv")
const props = defineProps({
  room: Object,

})

const { t: $t } = i18n.global;

// new walk
contextMenuItems.value.push({
  label: $t('New Walk-In Reservation'), icon: 'pi pi-copy',
  command: function () {
    const data =
    {
      is_walk_in: 1,
      arrival_date: moment(pageData.filters.value.date).toDate(),
      departure_date: moment(pageData.filters.value.date).add(1, "days").toDate(),
      room_type_id: props.room.room_type_id,
      room_id: props.room.name
    }
    window.postMessage({ "action": "new_fit_reservation", data: data }, "*")

  }
})

// new fit
contextMenuItems.value.push({
  label: $t('New FIT Reservation'), icon: 'pi pi-copy',
  command: function () {
    const data =
    {
      arrival_date: moment(pageData.filters.value.date).toDate(),
      departure_date: moment(pageData.filters.value.date).add(1, "days").toDate(),
      room_type_id: props.room.room_type_id,
      room_id: props.room.name
    }
    window.postMessage({ "action": "new_fit_reservation", data: data }, "*")

  }

})
// assign existing reservation
contextMenuItems.value.push({
  label: $t('Assign to Existing Reservation'), icon: 'pi pi-copy',
  command: function () {
    dialog.open(ComAssignReservationStayToRoom, {
      data: {
        room: props.room,
        date: moment(pageData.filters.value.date).format("YYYY-MM-DD")
      },
      props: {
        header: $t('Assign Reservation to this Room') + " - " + props.room.room_number,
        style: {
          width: '75vw',
        },
        modal: true,
        position: 'top',
        closeOnEscape: false,
        breakpoints: {
          '960px': '50vw',
          '640px': '100vw'
        },
      },
      onClose: (options) => {
        const result = options.data;
        if (result) {
          window.postMessage({ "action": "FloorPlanView" }, "*")

        }
      }
    })
  }

})


contextMenuItems.value.push({
  label: $t('Block this Room'), icon: 'pi pi-copy',
  command: function () {

    if (!gv.cashier_shift?.name) {
      gv.toast('error', 'Please Open Cashier Shift.')
      return
    }
    dialog.open(ComEditRoomBlock, {
      data: { date: moment(pageData.filters.value.date).toDate(), room_id: props.room.name },
      props: {
        header: 'Add New Room Block ',
        style: {
          width: '50vw',
        },
        modal: true,
        position: 'top',
        closeOnEscape: false,
        breakpoints: {
          '960px': '50vw',
          '640px': '100vw'
        },
      },
      onClose: (options) => {
        const result = options.data;
        if (result) {
          window.postMessage({ "action": "FloorPlanView" }, "*")
          window.postMessage("view_room_block_detail|" + result.name, "*")
        }
      }
    })
  }

})
const onOpenMenu = (event) => {
  menu.value.show(event);
};


</script>