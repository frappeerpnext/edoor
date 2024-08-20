<template>
  <ComFrontDeskLayout
    :showRefreshButton="true"
    :showSetting="true"
    :title="$t('Floor Plan View')"
    :showActionButton="!editMode"
    @onRefresh="getFloorPlanData(filters)"
  >
    <template #title>
      <div class="flex">
        <div class="text-xl md:text-2xl white-space-nowrap">
        {{ $t("Floor Plan View") }}
      </div>
      <div class="ml-8 header-title text-xl md:text-2xl white-space-nowrap">
        {{ moment.utc(filters.date).format("DD MMM, yyyy") }}
      </div>
      </div>
      
    </template>
    <template #setting_menu>
      <button
        v-if="!isMobile"
        @click="onEnableArrangeFloorPlan"
        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround"
      >
        <i class="pi pi-cog me-2"></i>
        {{ $t("Floor Plan Setting") }}
      </button>
    </template>

    <template #action>
      <template v-if="editMode">
        <Button class="border-none" @click="onAddElement">
        <i class="pi pi-plus me-2" />  
          {{$t('Add Element')}}</Button>
        <Button class="border-none" @click="onSavePosition">
          <i class="pi pi-external-link me-2" />
          {{ $t('Bulk Update Height & width') }}
          </Button>
        <Button class="border-none bg-red-500" @click="onCancelArrangePosition">
          <i class="pi pi-times me-2" />
          {{ $t('Cancel') }}
          </Button>
        <Button class="border-none" :disabled="gv.loading" @click="onSavePosition">
          <img class="pi pi-check-circle mr-2"  :src="BtnOkIcon" style="height: 13px;"/>
          {{ $t('Save Setting') }}
          </Button
        >
      </template>
    </template>

    <ComFilter @onFilter="getFloorPlanData" @onSearch="onSearch" />
    
    <ComRenderRoomDesktop
      v-if="!isMobile"
      :roomList="roomList"
      :editMode="editMode"
      :filters="filters"
      @onAddElement="onAddElement" 
    />
    <ComRenderRoomMobile v-else
    :roomList="roomList"
      :filters="filters"
    />
  </ComFrontDeskLayout>
    

</template>

<script setup>
import BtnOkIcon from '@/assets/svg/icon-save.svg' 
import {
  ref,
  getApi,
  onMounted,
  postApi,
  inject,
  onUnmounted,
  computed,
  useDialog,
  provide,
  getDoc
} from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComFilter from "@/views/floor_plan_view/components/ComFilter.vue";

import ComRenderRoomDesktop from "@/views/floor_plan_view/components/ComRenderRoomDesktop.vue";
import ComRenderRoomMobile from "@/views/floor_plan_view/components/ComRenderRoomMobile.vue";
import ComSelectElement from "@/views/floor_plan_view/components/ComSelectElement.vue";
import ComConfirmCheckIn from "@/views/reservation/components/confirm/ComConfirmCheckIn.vue"
import { i18n } from "@/i18n";
import { useConfirm } from "primevue/useconfirm";
import ComUnblockRoom from "@/views/room_block/components/ComUnblockRoom.vue"
const confirm = useConfirm()
const { t: $t } = i18n.global;
const filters = ref([]);
const room_list = ref([]);

const editMode = ref(false);
const moment = inject("$moment");
const gv = inject("$gv");
const isMobile = ref(window.isMobile);
const dialog = useDialog();
const background = ref()
provide("pageData", { filters: filters, roomList: room_list });

const roomList = computed(() => {
  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase();
    return room_list.value.filter(
      (r) =>
        (r.room_number || "").toLowerCase().includes(keyword) ||
        (r.stay?.guest_name || "").toLowerCase().includes(keyword)
    );
  } else {
    return room_list.value;
  }
});

function onEnableArrangeFloorPlan() {
  editMode.value = !editMode.value;
}

function test(){
  
  update_element_size()
}

function onSearch(keyword) {
  filters.value.keyword = keyword;
}

function getFloorPlanData(f) {
  gv.loading = true;
 

  // code read from databases
  getApi("frontdesk.get_floor_plan_data", {
    filters: {
      property: property_name,
      floor: f.floor,
      date: moment(f.date).format("YYYY-MM-DD"),
      floor_changed: f.floor != filters.value.floor,
      building: f.building,
    },
  })
    .then((result) => {
      if (f.floor != filters.value.floor) {
        room_list.value = result.message.floor_data.rooms;
        // we use --background-img for floor plan background url
        document.documentElement.style.setProperty('--background-img', `url('${result.message.floor_data.background}')`);
        gv.loading = true;
      }
      
      room_list.value.forEach((r) => {
        if (!window.isMobile){
          update_element_size(r)
        }
        

        r.stay = result.message.reservation_stays.filter(
          (x) => x.room_id == r.name
        );
      });

      filters.value = JSON.parse(JSON.stringify(f));
      gv.loading = false;
    })
    .catch((error) => {
      gv.loading = false;
    });
}
function update_element_size(room){

  if(window.isMobile){
    return
  }

    const width = document.querySelector(".container").offsetWidth
  const height = document.querySelector(".container").offsetHeight

  if(room){

    if(room.xp){
      room.x = room.xp*width
      
    }
    
    if(room.yp){
      room.y = room.yp*height
    }
    
    if(room.hp){
      room.height = room.hp*height
    }
    
    if(room.wp){
     
      room.width = room.wp*width
    }

  }else { 
     
  room_list.value.forEach(r=>{
    if(r.xp){
    
      r.x = r.xp*width

    }
    
    if(r.yp){
      r.y = r.yp*height
    }
 
    if(r.hp){
      r.height = r.hp*height
    }
    
    if(r.wp){
      r.width = r.wp*width
      r.container_width = width
       
    }

    
    

  })
}

  

}

function onAddElement(event) {
  dialog.open(ComSelectElement, {
    props: {
      header: $t("Select Element"),
      style: {
        width: "70vw",
      },
      modal: true,
      closeOnEscape: true,
      position: "center",
      breakpoints: {
        "960px": "650px",
        "640px": "100vw",
      },
    },
    onClose: (options) => {
      if (options.data) {
        room_list.value.push({
          element: options.data.innerHTML,
          x: 100,
          y: 100,
          height: 100,
          width: 100,
        });
      }
    },
  });
}

function onSavePosition() {
  const width = document.querySelector(".container").offsetWidth
  const height = document.querySelector(".container").offsetHeight
  gv.loading = true;
  postApi("frontdesk.save_room_layout_position", {
    floor: filters.value.floor,
    data: room_list.value.filter(r=>(r.is_deleted || 0)==0).map((r) => {
      const d = {
        name: r.name,
        x: r.x,
        y: r.y,
        width: r.width,
        height: r.height,
        xp:r.x/width,
        yp:r.y/height,
        wp:r.width/width,
        hp:r.height/height,
        element: r.element,
        z_index: r.z_index || 0,
      };
      if (d.element == "" ) {
        delete d["element"];
      }
      return d;
    }),
  })
    .then((r) => {
      editMode.value = false;
      gv.loading = false;
      // window.location.reload();
    })
    .catch((error) => {
      gv.loading = false;
    });
}

function onCancelArrangePosition(){
  const f = JSON.parse(JSON.stringify(filters.value))
  filters.value.floor="dummayr"
  getFloorPlanData(f)
  editMode.value = false

}
const actionRefreshData = async function (e) {
  if (e.isTrusted && typeof e.data != "string") {
    if (e.data.action == "FloorPlanView" || e.data.action == "Frontdesk") {
      getFloorPlanData(filters.value);
    } else   if (e.data.action == "Check In from Floor Plan View") {
      checkIn(e.data.data)
    }
    else   if (e.data.action == "Check Out from Floor Plan View") {
      onCheckOut(e.data.data)
    }
    else   if (e.data.action == "Unblock Room from Floor Plan View") {
      onUnBlockRoom(e.data.data)
    }
  }
};

function checkIn(data){
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
                reservation: data.reservation,
                reservation_stays: [data.reservation_stay],
                note: result.note,
                arrival_time: result.checked_in_date
              }).then((result) => {
                gv.loading = false
                getFloorPlanData(filters.value);
              })
                .catch((err) => {
                  gv.loading = false
                })
            }
          }
        })
}
function onCheckOut(data) {
    confirm.require({
        message: 'Are you sure you want to check out this room?',
        header: 'Confirmation',
        acceptLabel: 'OK',
        rejectVisible: true,
        rejectClass: 'hidden',
        acceptClass: 'border-none',
        acceptIcon: 'pi pi-check-circle',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            gv.loading = true
            postApi("reservation.check_out", {
              reservation: data.reservation,
              reservation_stays: [data.reservation_stay]
            }, "Check out successfully")
                .then((result) => {
                  gv.loading = false
                  getFloorPlanData(filters.value);
                })
                .catch((err) => {
                  gv.loading = false
                })
        }
    });
}
function onUnBlockRoom(data){
  if(window.isMobile){
          const elem = document.querySelector(".p-dialog");
          elem?.classList.add("p-dialog-maximized"); // adds the maximized class

      }
      getDoc("Room Block",data.room_block_name).then(doc=>{
        doc.unblock_date = moment(data.date).toDate()
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
                getFloorPlanData(filters.value);
              }
          })
      })
}
// Create a ResizeObserver instance
const resizeObserver = new ResizeObserver(entries => {
    for (let entry of entries) {
    
          update_element_size()
            
    }
});



// Start observing the div element


onMounted(() => {
  window.addEventListener("message", actionRefreshData, false);
  if (!window.isMobile) {
    const divElement = document.querySelector('.container');

  resizeObserver.observe(divElement);
  }

});
onUnmounted(() => {
  window.removeEventListener("message", actionRefreshData, false);
});
</script>
