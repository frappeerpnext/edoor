<template>
    <div v-if="data">
        <div class="grid w-full" >
            <div class="col-3">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <h3 class="text-lg font-medium">Reservation</h3>
                    <div  class="w-full " >
                    <ComChartByReservation :param="data"/>
                    </div>
                </div>
            </div>
            <div class="col-3">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <h3 class="text-lg font-medium"> Stay by Business Source</h3>
                    <div  class="w-full " >
                        <ComChartByBusinessSource :param="data.reservation_by_business_source"/>
                    </div>
                </div>
            </div>
            <div class="col-3">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <h3 class="text-lg font-medium">Stay by Room Type</h3>
                    <div  class="w-full " >
                        <ComChartByRoomType :param="data.reservation_by_room_type"/>
                    </div>
                </div>
            </div>
            <div class="col-3">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <h3 class="text-lg font-medium">Stay by Reservation Type</h3>
                    <div  class="w-full " >
                        <ComChartByReservationType :param="data"/>
                    </div>
                </div>

            </div>
        </div>
<ComBarChartSummary :data="data" />   
</div>



</template>

<script setup>
import { ref,onMounted,getApi,inject } from '@/plugin';
import ComChartByReservation from '@/views/property_summary/components/ComChartByReservation.vue'; 
import ComChartByReservationType from '@/views/property_summary/components/ComChartByReservationType.vue'; 
import ComChartByBusinessSource from '@/views/property_summary/components/ComChartByBusinessSource.vue'; 
import ComChartByRoomType from '@/views/property_summary/components/ComChartByRoomType.vue'; 
import ComBarChartSummary from '@/views/property_summary/components/ComBarChartSummary.vue'; 

const data = ref()
const loading = ref(false)

const props = defineProps({
    property:String,
    date:String,
    room_type_id:String
})
 
onMounted(()=>{
    loading.value = true 
    setTimeout(function(){
        getApi("frontdesk.get_dashboard_data",{
        property:props.property,
        date:props.date,
        room_type_id:props.room_type_id,
        include_reservation_by_business_source:1,
        include_reservation_by_room_type:1

        
    }).then(r=>{
        data.value = r.message
        loading.value = false
    }).catch(err=>{
        loading.value = false
    })
    },500)
    


})
</script>