<template>
    
    {{ op.all_reservation_data?.data.length }}
 
        <div class="card">
            <DataTable 
                :value="op.all_reservation_data?.data" 
                tableStyle="min-width: 50rem" 
                :is-not-empty="op.all_reservation_data?.data.length > 0"
                >
                <template #header>
                    <div class="flex flex-wrap align-items-center justify-content-between gap-2">
                        <span class="text-xl text-900 font-bold">Products</span>
                        <!-- <Button icon="pi pi-refresh" rounded raised /> -->
                    </div>
                </template> 
                <Column header="Guest">
                    <template #body="slotProps">
                        {{ slotProps.data.guest_name }}
                    </template>
                </Column>
            </DataTable>
        </div>
</template>

<script setup>
import { inject, ref, useRoute,watch ,onMounted,postApi} from '@/plugin';

const route = useRoute()

const op = inject("$operation_dashboard")
const moment = inject("$moment")
op.page_title = route.meta.title
op.current_route = route.name

const data = ref([])

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

function loadData(){
    postApi("operation_dashboard.get_arrival_guest",{
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
      
        loadData()
    }
    
    
})

</script>