<template> 
    <div class="w-full h-full  p-2  relative">
      <div class="flex absolute right-1 top-1 gap-2">
<div  v-tippy="{ content: stay.business_source, placement: 'left' }" style="width:20px;height:20px;background-color: #fff;" class="text-center border-1 overflow-hidden border-round-lg box-shadow-floor-item">
        <img v-if="stay.business_source_photo" :src="stay.business_source_photo" />
        <span style="color:#999999" class="text-center font-semibold" v-else>
          {{stay.business_source.charAt(0)}}
        </span>
      </div>
      </div>

        <div class="line-height-1 px-2">
          
     <div class="text-lg  font-medium">{{ room?.room_type_alias }} - {{ room.room_number }}</div>
     <div class="w-full text-overflow-ellipsis">
      {{ stay.guest_name }}
     </div>
     <div class="mt-1">
        <i v-tippy="{ content: stay?.reservation_type, placement: 'left' }" :class="stay?.reservation_type == 'FIT' ? 'pi-user' : 'pi-users'" class="pi me-1"></i>  
        <span>{{stay?.adult}}</span>/<span>{{stay?.child}}</span> 
        <span class="my-2">
          |
        </span>
        
        <i class="pi pi-calendar me-1"></i>  
        <span>{{stay?.room_nights}}</span> 
     </div> 
        </div>
        <div class="mt-auto">
  <hr class="my-2">
        </div>
        <div class="flex gap-1">
            <ComChipIcon v-tippy="{ content: room?.housekeeping_status_code, placement: 'left' }" svgIcon="broom" iconHeight="12px" :bgColor="room?.status_color" />
            <ComChipIcon v-tippy="{ content: 'Arrival', placement: 'left' }" v-if="stay?.is_arrival" svgIcon="iconArrival" iconHeight="12px" bgColor="#4299e1" />
            <ComChipIcon v-tippy="{ content: 'Departure', placement: 'left' }" v-if="stay?.is_departure" svgIcon="icondeparture" iconHeight="12px" bgColor="#878787" />
            <ComChipIcon v-tippy="{ content: 'Stay Over', placement: 'left' }" v-if="stay?.is_stay_over" svgIcon="iconstayover" iconHeight="12px" bgColor="#00b3b6" />
            <ComChipIcon v-tippy="{ content: stay?.pick_up ? 'Pick Up' : 'Drop Off', placement: 'left' }" v-if="stay?.pick_up || stay?.drop_off" icon="pi-car" iconHeight="9" bgColor="#8aa5ff" />
            <ComChipIcon v-tippy="{ content: 'This Room Have Other Reservation', placement: 'left' }" v-if=" room.stay.length > 1" icon="pi-info" iconHeight="9" bgColor="#869e00" />
            
        </div>

    </div>
    
</template>
  
  <script setup>
  import { defineProps, defineEmits } from 'vue';
  import { useTippy } from "vue-tippy";
  import ContextMenu from 'primevue/contextmenu';
  import ComChipIcon from '@/views/floor_plan_view/components/ComChipIcon.vue'
  const props = defineProps({
    stay: {
      type: Object,
      required: true
    },
    room: {
      type: Object,
      required: true
    }
  });
  
  
  </script>
  