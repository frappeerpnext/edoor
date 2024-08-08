<template>
  <ComFrontDeskLayout :showRefreshButton="true" :showSetting="true" :title="$t('Floor Plan View')"
  :showActionButton="!editMode" 
  @onRefresh="getFloorPlanData(filters)"
  >
  <template #title>
    <div   class="text-xl md:text-2xl white-space-nowrap">{{$t('Floor Plan View')}}</div> 
    <div class="ml-8 header-title text-xl md:text-2xl white-space-nowrap">{{moment.utc(filters.date).format('DD MMM, yyyy')}}</div>
  </template>
    <template #setting_menu>
      <button
        @click="onEnableArrangeFloorPlan"
        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround"
      >
        <i class="pi pi-cog me-2"></i>
        {{ $t("Floor Plan Setting") }}
      </button>
    </template>
    <template #action>
      <template v-if="editMode">
        <Button   @click="onSavePosition">Add Element</Button>
        <Button   @click="onSavePosition">Change Background</Button>
        <Button   @click="onSavePosition">Bulk Update Height & width</Button>
        <Button   >Cancel</Button>
        <Button :disabled="gv.loading"  @click="onSavePosition">Save Setting</Button>
        
      </template>
      
    </template>

    <ComFilter @onFilter="getFloorPlanData" @onSearch="onSearch" />

    <ComRenderRoomDesktop v-if="!isMobile" :roomList="roomList" :editMode="editMode" :filters="filters" />

    
  </ComFrontDeskLayout>
</template>

<script setup>
import { ref, getApi, onMounted, postApi, inject,onUnmounted,computed } from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComFilter from "@/views/floor_plan_view/components/ComFilter.vue";

import ComRenderRoomDesktop from "@/views/floor_plan_view/components/ComRenderRoomDesktop.vue";
import { i18n } from "@/i18n";
 

const { t: $t } = i18n.global;
const filters = ref([]);
const room_list = ref([]);
 
const editMode = ref(false);
const moment = inject("$moment");
const gv = inject("$gv")
const isMobile = ref(window.isMobile)

const roomList = computed(()=>{
  if(filters.value.keyword){
    const keyword = filters.value.keyword.toLowerCase()
    
    return room_list.value.filter(r=> 
        (r.room_number || '').toLowerCase().includes(keyword) ||
        (r.guest_name || '').toLowerCase().includes(keyword) 
    )
  }else {
    return room_list.value
  }
})

function onEnableArrangeFloorPlan() {
  editMode.value = !editMode.value;

}




function onSearch(keyword){
  filters.value.keyword = keyword
}

function getFloorPlanData(f) {
 
  gv.loading = true
  // code read from databases
  getApi("frontdesk.get_floor_plan_data", {
    filters: {
      property: property_name,
      floor: f.floor,
      date: moment(f.date).format("YYYY-MM-DD"),
      floor_changed: f.floor != filters.value.floor,
      building: f.building
    },
  }).then((result) => {
    if (f.floor != filters.value.floor) {
      room_list.value = result.message.room_list;
gv.loading = true
    }
    room_list.value.forEach(r => {
        r.stay = result.message.reservation_stays.find(x=>x.room_id == r.name)
    });
    
    filters.value = JSON.parse(JSON.stringify(f));
    gv.loading = false
  }).catch(error=>{
    gv.loading  = false
  });
}

function onSavePosition() {
  gv.loading = true
  postApi("frontdesk.save_room_layout_position", {
    floor: filters.value.floor,
    data: room_list.value.map((r) => {
      return {
        name: r.name,
        x: r.x,
        y: r.y,
        width: r.width,
        height: r.height,
      };
    }),
  }).then((r) => {
    editMode.value = false;
    gv.loading = false
  }).catch(error=>{
    gv.loading = false
  });
}


const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if (e.data.action == "FloorPlanView" || e.data.action == "Frontdesk") {
          
          getFloorPlanData(filters.value)

        }
    };
}

onMounted(() => {
  window.addEventListener('message', actionRefreshData, false);
});
onUnmounted(() => {
  window.addEventListener('message', actionRefreshData, false);
});

</script>

