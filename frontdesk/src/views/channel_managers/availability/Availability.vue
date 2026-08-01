<template>
    <div>
        <ComHeader :isRefresh="true" @onRefresh="onRefresh" :settingMenus="settingMenus" isSetting>
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center justify-content-between w-full">
                        <div class="text-xl md:text-2xl white-space-nowrap">{{ $t('Availability') }}</div>

                    </div>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2 w-full justify-content-end">
                      <Button  
                v-if="cmInfo?.enable == 1 && cmInfo?.rooms_availability == 'Receive from PMS'"

                icon="pi pi-sync" :label="$t('Resync Availability')" 
                @click="onResyncAvailability"
                />

                    <SplitButton icon="pi pi-chart-line"  label="Report" @click="onReportClick" :model="actionMenus" />
                  
                </div>
            </template>
        </ComHeader>


        <ComFilter class="mb-3" :hideSearchField="true" @onSearch="onFilter" :filters="filterOptions" v-model:filter="filters">
            <template #dates v-if="filters?.dates">

                {{ moment(filters?.dates[2][0]).format("DD-MM-YYYY") }} to
                {{ moment(filters?.dates[2][1]).format("DD-MM-YYYY") }}
            </template>
            <template #rate_type v-if="filters?.rate_type">
                {{ filters?.rate_type[2] }}
            </template>
        </ComFilter>

        <div>

            <ComRoomAvailabilityGrid />

        </div>
    </div>
</template>
<script setup>

import ComRoomAvailabilityGrid from "@/views/channel_managers/availability/components/ComRoomAvailabilityGrid.vue"
import ComFilter from "@/components/document/components/ComFilter.vue"
import ComReSyncAvailability from "@/views/channel_managers/availability/components/ComReSyncAvailability.vue"


import { inject, onMounted, onUnmounted, ref } from "vue";
import { i18n } from '@/i18n';
import { useAvailability } from "@/views/channel_managers/availability/hooks/useAvailability.js";
const { t: $t } = i18n.global;

import { useApp } from "@/hooks/useApp.js";
const moment = inject("$moment")
const settingMenus = [
    {
            label: $t('Verital Calendar View'),
            icon: 'pi pi-calendar',
            command: () => {
                alert(123)
            }
        },
    {
            label: $t('Horizontal Calendar View'),
            icon: 'pi pi-list',
            command: () => {
                alert(123)
            }
        },
] 

const {cmInfo} = useApp()
 

const filterOptions = ref([
    { fieldname: "dates", label: "Date", fieldtype: "Date", hideOperator: true, operator: "Between", default: [moment().toDate(), moment().add(1, "year").toDate()], showYearSelection: true,maxSelectDate:366 },

    // { fieldname: "departure_date", label: "Departure" },
    { fieldname: "room_types", label: "Room Types", fieldtype: 'Link', options: 'Room Type', operator: "in", hideOperator: true },
    { fieldname: "rate_type", label: "Rate Plan", fieldtype: 'Link', options: 'Rate Type', operator: "=", hideOperator: true, filters: [["is_complimentary", "=", 0], ["is_house_use", "=", 0]], require: true },


])

const {
    oldFitlers,
    filters,
    onRefresh,
resetData,
    
    updateAvailabiltyRestricion,
    getData,
   

    getCloseRestrictionData
} = useAvailability();




async function onFilter(f) {

    const change_filter = app.utils.compareJSON(oldFitlers.value, f)


    const l = await window.showLoading();
    if (change_filter?.dates) {
        await getData();
        await getCloseRestrictionData();
    } else {
        if (change_filter?.rate_type) {
            await getCloseRestrictionData();
        }
    }

    oldFitlers.value = JSON.parse(JSON.stringify(f));
    l.close();


}

function onResyncAvailability(){
    const result = app.utils.openDialog(ComReSyncAvailability,"Resync Room Availability")
}

function onReportClick(){
    app.dialog.viewReport("/Reservation/rptRoomInventory",$t("Room Inventory"),
             [
                        {name: 'start_date', values: [moment.utc(filters.value.dates[2][0]).format("YYYY-MM-DD")] },
                        {name: 'end_date', values: [moment.utc(filters.value.dates[2][1]).format("YYYY-MM-DD")] },
                        {name: 'property', values: [window.propert_name] },
                        
                        
                ]
)
}
const actionMenus = [
    {
        label: 'Room Inventory Report',
        command: () => {
            app.dialog.viewReport("/Reservation/rptRoomInventory",$t("Room Inventory"),
             [
                        {name: 'start_date', values: [moment.utc(filters.value.dates[2][0]).format("YYYY-MM-DD")] },
                        {name: 'end_date', values: [moment.utc(filters.value.dates[2][1]).format("YYYY-MM-DD")] },
                        {name: 'property', values: [window.propert_name] },
                        
                        
                ]

        )
           

        }
    },
    {
        label: 'Inventory Room Booked Report',
        command: () => {
             app.dialog.viewReport("/Reservation/rptRoomInventoryRoomBooked",$t("Inventory Room Booked"),
             [
                        {name: 'start_date', values: [moment.utc(filters.value.dates[2][0]).format("YYYY-MM-DD")] },
                        {name: 'end_date', values: [moment.utc(filters.value.dates[2][1]).format("YYYY-MM-DD")] },
                        {name: 'property', values: [window.propert_name] },
                        
                        
                ]

        )

        }
    },
]


onUnmounted(()=>{
    resetData()
})



 

</script>
