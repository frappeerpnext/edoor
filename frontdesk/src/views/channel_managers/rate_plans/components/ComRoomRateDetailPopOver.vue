<template>
    <div>
        <div v-if="isLoading" class="popover-loading">
            Loading...
        </div>

        <div v-else>
            <h1 class="text-xl">{{ moment(date).format("DD-MM-YYYY") }}</h1>
            
            <!-- Rate Table -->
            <DataTable
                :value="tableRows"
                scrollable
                scrollHeight="400px"
                class="p-datatable-sm"
            >

                <!-- Occupancy Column -->
                <Column
                    field="title"
                    header="Occupancy"
                    frozen
                    style="min-width:200px"
                />

                <!-- Dynamic Room Type Columns -->
                <Column
                    v-for="rt in roomTypes"
                    :key="rt.name"
                    :field="rt.name"
                    :header="rt.room_type"
                    style="min-width:75px"
                >
                    <template #body="slotProps">
                        <div class="text-center">
                            <template v-if="['Closed','Cta','Ctd'].includes(slotProps.data.title)"> 
                                <template v-if="slotProps.data[rt.name]">
                                    <Chip label="Closed" v-if="slotProps.data[rt.name] == '1'" class="text-red-400"/>
                                    <Chip label="Opened" class="text-green-400" v-else/>
                                
                                </template>
                                <span v-else>-</span>
                                
                            </template>
                            <template v-else-if="slotProps.data.title == 'FullPatternLos'">
                                <span v-if="slotProps.data[rt.name]">
                                    {{ ( slotProps.data[rt.name].match(/O/g) || []).length }}
                                </span>
                                <span v-else>-</span>
                            </template>
                            <template v-else>
                                <template v-if="slotProps.data.group == 'Rate'">
                                    
                                    <CurrencyFormat :value="slotProps.data[rt.name]" v-if="slotProps.data[rt.name]"/>
                                        <span v-else>-</span>
                                
                                </template>
                                <span v-else>{{ slotProps.data[rt.name] ?? '-' }}</span>

                                
                            </template>
                        </div>
                    </template>
                </Column>

            </DataTable>

        </div>
    </div>
</template>

<script setup>
import { onMounted, ref, computed, inject } from 'vue';
const moment = inject("$moment")
const props = defineProps({
    date: Object,
    rate_type: String,
    room_type_id: String
})

const data = ref()
const isLoading = ref(true)

/* ---------------------------
   Build Room Type Columns
--------------------------- */

const roomTypes = computed(() => {
    if (!data.value) return []

    return [...data.value.room_types]
        .sort((a, b) => a.sort_order - b.sort_order)
})


/* ---------------------------
   Build Table Rows
--------------------------- */

const tableRows = computed(() => {

    if (!data.value) return []

    const occCodes = [...data.value.occupancy_codes]
        .sort((a, b) => a.sort_order - b.sort_order)

    const rates = data.value.room_rate

    const rows =  occCodes.map(occ => {

        const row = {
            group:"Rate",
            occupancy_code: occ.name,
            title: occ.title
        }

        roomTypes.value.forEach(rt => {

            const found = rates.find(r =>
                r.rt === rt.name &&
                r.occ === occ.name
            )

            row[rt.name] = found
                ? found.rate
                : null

        })
        return row
    })

    const restriction_types =  [...new Set(data.value.restriction.map(item => item.restriction_type))]
    restriction_types.forEach(r=>{
        let _row = {
            title:r,
            group:"Restriction"
        }
        data.value.room_types.forEach(rt=>{
            _row[rt.name] = data.value.restriction.find(x=>x.restriction_type == r && x.room_type_id==rt.name)?.value
        })
        rows.push(_row)
    })

    return rows

})


/* ---------------------------
   API Call (unchanged)
--------------------------- */

async function getRoomRateDetail() {

    isLoading.value = true

    const res = await app.getApi(
        "rate_plan.get_room_rate_detail",
        {
            property: window.property_name,
            rate_type: props.rate_type,
            date: props.date
        }
    )

    if (res.data) {
        data.value = res.data
    }

    isLoading.value = false
}


onMounted(async () => {

    setTimeout(async () => {
        await getRoomRateDetail();
    }, 1000)

})
</script>