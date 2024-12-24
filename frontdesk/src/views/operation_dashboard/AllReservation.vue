<template>
    <ComFilterOption />
        <div class="card">
            
            <DataTable 
                 
                :value="op.all_reservation_data?.data" 
                tableStyle="min-width: 50rem" 
                :is-not-empty="op.all_reservation_data?.data.length > 0"
                rowGroupMode="subheader" 
                groupRowsBy="guest_name" 
                selectionMode="single"
                :selection="selectedRow"
                v-model:expandedRows="expandedRows"
              @row-select="onRowSelect"
                @row-dblclick="onRowDoubleClick"

             
                >
                
                <Column header="Guest">
                    <template #body="slotProps">
                        <ComGuestCard :data="slotProps.data" />
                    </template>
                </Column>
                <Column header="Accomodation">
                    <template #body="slotProps">
                        <ComAccomodationCard :data="slotProps.data" />
                    </template>
                </Column>
                
                
                <Column header="Stay Info">
                    <template #body="slotProps">
                        <ComStayInfoCard :data="slotProps.data" />
                    </template>
                </Column>
                <Column header="Status">
                    <template #body="slotProps">
                        <ComReservationStayStatus :data="slotProps.data" />
                    </template>
                </Column>
                <Column header="">
                    <template #body="slotProps">
                        <ComStayAction :data="slotProps.data" />
                    </template>
                </Column>
                <template #expansion="slotProps">
                    <div class="p-3">
                        Detail Action list here
</div>
                </template>
                <template #groupheader="slotProps">
                   <ComGroupInfo :data="slotProps.data" group_by="guest_name"/>
                </template>
             
            </DataTable>
        </div>
</template>

<script setup>
import { inject, ref, useRoute,watch ,onMounted,getApi,postApi} from '@/plugin';
import ComGuestCard from "@/views/operation_dashboard/components/ComGuestCard.vue"
import ComAccomodationCard from "@/views/operation_dashboard/components/ComAccomodationCard.vue"
import ComStayInfoCard from "@/views/operation_dashboard/components/ComStayInfoCard.vue"
import ComReservationStayStatus from "@/views/operation_dashboard/components/ComReservationStayStatus.vue"
import ComStayAction from "@/views/operation_dashboard/components/ComStayAction.vue"
import ComFilterOption from "@/views/operation_dashboard/components/ComFilterOption.vue"
import ComGroupInfo from "@/views/operation_dashboard/components/ComGroupInfo.vue"
// import ComAccomodationCard from "@/views/operation_dashboard/components/ComAccomodationCard.vue"
const route = useRoute()

const op = inject("$operation_dashboard")
const moment = inject("$moment")
op.page_title = route.meta.title
op.current_route = route.name
const selectedRow = ref()
const data = ref([])
const expandedRows = ref(null);
// date change
watch(
    () => op.current_date,
    (new_data) => {
        loadData()
    }
);

// refresh
watch(
    () => op.refresh_token,
    (new_data) => {
        loadData()
    }
);

const onRowSelect = (event) => {
  
expandedRows.value = [event.data];
};



function loadData(){
    postApi("operation_dashboard.get_all_guest",{
        filter:{ 
        property:window.property_name,
        date:moment(op.current_date).format("YYYY-MM-DD"),
        }
    },"",false).then(result=>{
        op.all_reservation_data.date = moment(op.current_date).format("YYYY-MM-DD")
        op.all_reservation_data.data = result.message
    })
}

onMounted(() => {
    
    if (moment(op.current_date).format("YYYY-MM-DD") != moment(op.all_reservation_data?.date).format("YYYY-MM-DD")){
        op.all_reservation_data.data = []
        alert("get data")
        loadData()
    }
    
    
})

function onRowDoubleClick(event) {
    const rowData = event.data;
    window.postMessage('view_reservation_stay_detail' + "|" + rowData.name, '*')
}

</script>