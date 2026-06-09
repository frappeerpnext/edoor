<template>
    <ComDialogContent hideButtonClose titleButtonOK="Ok" :hideIcon="false" :hideButtonOK="true" >
<Message>
    The following data is pending synchronization with the channel manager. Data sync to the server is scheduled every 5 minutes. If it is not synchronized with the channel manager, please contact your system administrator.
</Message>
        <div v-if="data?.room_rates.length>0">
            <h1 class="text-3xl">Room Rates</h1>
            <div v-for="rr in data.room_rates">
                <h1 class="text-2xl">{{ rr.rate_type }}</h1>
                <DataTable :value="rr.data" stripedRows responsiveLayout="scroll">



                    <Column field="room_type" header="Room Type" />

                    <Column field="period" header="Periods">
                        <template #body="slotProps">

                            <span class="font-medium">
                                <div v-for="d in slotProps.data.period">
                                    {{ moment(d.start_date).format("DD-MM-YYYY") }} to {{
                                        moment(d.end_date).format("DD-MM-YYYY") }}
                                </div>

                            </span>

                        </template>
                    </Column>
                    <Column field="rate" header="Rate">
                        <template #body="slotProps">

                            <span class="font-medium">
                                <div v-for="r in slotProps.data.rates">

                                    <CurrencyFormat :value="r.rate"></CurrencyFormat> / {{ r.title }}
                                </div>

                            </span>

                        </template>
                    </Column>

                </DataTable>
            </div>
        </div>
        <div v-if="data?.restrictions.length>0">
            <h1 class="text-3xl">Restrictions</h1>
            <div v-for="r  in data.restrictions">
                <h1 class="text-2xl">{{ r.rate_type }}</h1>
                <DataTable :value="r.data" stripedRows responsiveLayout="scroll">



            <Column field="restriction_type" header="Restriction Type" />
            <Column field="room_type" header="Room Type" />

            <Column header="Periods">
              <template #body="slotProps">
                <span class="font-medium">
                  
                    {{ moment(slotProps.data.start_date).format("DD-MM-YYYY") }} to {{ moment(slotProps.data.end_date).format("DD-MM-YYYY") }}
                  

                </span>

              </template>
            </Column>
            <Column field="value" header="Value">
              <template #body="slotProps">
 
                <span class="font-medium">
                  <template v-if="['Closed','Cta','Ctd'].includes(slotProps.data.restriction_type)">
                    <Chip label="Closed" v-if="slotProps.data.value === '1'" icon="pi pi-times" :class="'bg-red-200' " />
                    <Chip label="Opened" icon="pi pi-check" :class="'bg-green-200'" v-else />
                  </template>
                  <template v-else>
                    {{ slotProps.data.value }}
                  </template>
                  
                </span>

              </template>
            </Column>

          </DataTable>
            </div>
        </div>
        <div v-if="data?.availabilities.length>0">
            <h1 class="text-3xl">Room Availability</h1>
 
                
                <DataTable :value="data?.availabilities" stripedRows responsiveLayout="scroll">



            <Column field="room_type_name" header="Room Type" />
            

            <Column header="Periods">
              <template #body="slotProps">
                <span class="font-medium">
                  
                    {{ moment(slotProps.data.start_date).format("DD-MM-YYYY") }} to {{ moment(slotProps.data.end_date).format("DD-MM-YYYY") }}
                  

                </span>

              </template>
            </Column>
            <Column field="value" header="Total Room Available" headerClass="text-center" bodyClass=""/>

          </DataTable>
            
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, onMounted, ref } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
const data = ref()
const moment = inject("$moment")
async function getData() {
    const l = await window.showLoading()
    const res = await app.getApi("edoor.channel_managers.utils.get_pending_sync_data", {
        property: window.property_name
    })
    if (res.data) {
        data.value = res.data
    }
    l.close();
}
onMounted(async () => {
    await getData()
})
</script>