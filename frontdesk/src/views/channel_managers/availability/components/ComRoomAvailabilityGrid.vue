<template>
    <div>
 
        <table class="rate-table" v-if="months" >
            <thead>
                <tr>
                    <th class="sticky-left header-cell left-header">Room Type</th>
                    <th v-for="n in numDays" class="header-cell text-center">{{ n }}</th>
                </tr>
            </thead>
            <tbody>
                <template v-for="m in months">
                    <tr>
                        <th lass="sticky-left month-cell text-left" >{{ moment(m.start_date).format("MMM - YYYY") }}  </th>
                        <td
                            class="dc"
                         v-for="n in numDays" :class="moment.utc(moment.utc(m.start_date).format('YYYY-MM-' + n)).format('D dd')"
                         
                         >
                            <div v-if="n<=m.max_days">{{ moment.utc(moment.utc(m.start_date).format("YYYY-MM-" + n)).format("D dd") }}</div>
                        </td>
                    </tr>
                    <tr v-for="rt in displayRoomTypes">
                        <th  lass="sticky-left month-cell text-left">
                           <div><strong> {{ rt.room_type }} ({{ rt.total_rooms }})</strong></div>
                           <div>Room Available</div>
                           <div>Occupy</div>
                           <div>Room Block</div>

                        </th>
                        <td class="dc" v-for="n in numDays" :class="moment.utc(moment.utc(m.start_date).format('YYYY-MM-' + n)).format('D dd')">
                            <div v-if="canShowValue(m,n)">
                              
                                
                           
                            <div>
                               
                                 <i class="pi pi-times text-red-400" v-if="restrictionValue(m,n,rt.name)"
                            style="font-size: 1rem"></i>
                            <i class="pi pi-check  text-green-400" v-else style="font-size: 1rem"></i>

                            </div>
                            <!-- room available -->
                            <div>
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}${rt.name}`)]?.total_available
                                }}
                            </div>
                            <!-- occupy -->
                            <div>
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}${rt.name}`)]?.occupy
                                }}
                            </div>
                            <!-- block -->
                            <div class="text-red-400">
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}${rt.name}`)]?.blocked
                                }}
                            </div>
                             </div>
                        </td>

                    </tr>
                    <tr style="border-top: solid 1px red;">
                        <td colspan="32">Total</td>
                    </tr>
                    <tr>
                        <th>
                           <div>{{ $t("Room Available") }}</div>
                           <div>{{ $t("Occupy") }}</div>
                           <div>{{ $t("Room Block") }}</div>
                           <div>{{ $t("Occupancy (%)") }}</div>

                        
                        </th>
                        <td v-for="n in numDays">
                            <!-- total room available -->
                            <div>
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}`)]?.total_available
                                }}
                            </div>
                            <!-- total  occupy -->
                            <div>
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}`)]?.occupy
                                }}
                            </div>
                            <!-- total block -->
                            <div class="text-red-400">
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}`)]?.blocked
                                }}
                            </div>
                            <div class="text-green-400">
                                {{
                                    data[moment(m.start_date).format(`YYMM${String(n).padStart(2,
                                        '0')}`)]?.occupancy
                                }}
                            </div>
                        </td>
                    </tr>

                </template>

            </tbody>

        </table>

    </div>



</template>
<script setup>
import { computed, inject } from 'vue';
import { useAvailability } from '../hooks/useAvailability';

const { data, roomTypes, filters,closeRestrictionData } = useAvailability()
const numDays = Array.from({ length: 31 }, (_, i) => i + 1)
const months = computed(() => {
    if(filters.value?.dates){
return app.utils.getMonthlyRanges(filters.value?.dates[2][0], filters.value?.dates[2][1])
    }
    return null
    
})
const moment = inject("$moment")
const displayRoomTypes = computed(()=>{
    if(filters.value.room_types){
        if(filters.value.room_types[2].length>0){
            return roomTypes.value.filter(x=>filters.value.room_types[2].includes(x.name) )
        }
    }
    return roomTypes.value;
})

function canShowValue(month,n){
    return  (
            moment.utc(moment.utc(month.start_date).format('YYYY-MM-' + n))>=moment.utc(moment.utc(filters.value.dates[2][0]).format("YYYY-MM-DD")) 
            &&
            moment.utc(moment.utc(month.start_date).format('YYYY-MM-' + n))<=moment.utc(moment.utc(filters.value.dates[2][1]).format("YYYY-MM-DD")) 
    )

}
function restrictionValue(month,n,room_type_id){
    return (closeRestrictionData.value?.Closed[moment(month.start_date).format(`YYMM${String(n).padStart(2,'0')}${room_type_id}`)] || 0)



}
</script>

<style scoped>
.table-wrapper {
    user-select: none;
    position: relative;
}

.disable {
    background: #f5f5f5 !important;
    color: #bbb;
    pointer-events: none;
}

.selected-cell {
    /* content: "";
  position: absolute;
  inset: 0; */
    background: #cfe5ff !important;
}

.selected-cell.Sa>.day-name,
.selected-cell.Su>.day-name {
    background: rgb(246, 253, 217);
    border-radius: 10px;
}

.drag-rect {
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    border: 2px dashed #409eff;
    background: rgba(64, 158, 255, 0.08);
    animation: dash-move 0.5s linear infinite;
    box-shadow: 0 0 6px rgba(64, 158, 255, 0.6);
}

.drag-rect.drag-rect-deselect {
    border: 2px dashed #f56c6c;
    background: rgba(245, 108, 108, 0.1);
}

.dc {
    transition: background-color 0.05s ease;
    position: relative;
    border-right-width: 1px;
    padding-right: 3px;
    padding-left: 3px;
}

.dc:hover {
    background-color: rgba(64, 158, 255, 0.05);
}

.Sa,
.Su {
    background: rgb(246, 253, 217);
}

.closed .day-name {
    background: #ff0000b1 !important;
    border-radius: 10px;
    color: #ffffff !important;
}

/* Popover styling */
.cell-popover {
    position: absolute;
    z-index: 10000;
    background: white;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 12px 16px;
    min-width: 200px;
    pointer-events: auto;
    font-size: 14px;
}

.popover-loading {
    color: #666;
    font-style: italic;
}

.rate-table {
    width: 100%;
}
.rate-table td {
    vertical-align: top;
}

.dc:not(.disable) .day-name {
    color: rgb(66, 66, 120);
}

.day-name {
    text-align: center;
    margin-bottom: 0.5rem;
    font-weight: bold;
    font-size: 10px;
}

.v {
    text-align: right;
}

.dc:not(.disable) .v {
    color: rgb(66, 66, 120);
}

.table-wrapper {
    margin-top: 20px;
}

.table-wrapper th {
    border-width: 1px;
    padding: 8px 0;
}

.rate-table>* {
    font-size: 12px !important;
}

.sticky-left.month-cell.text-left {
    padding-left: 5px;
}

.table-wrapper th {
    background: #e9e9ff;
}

.rate-table>thead {
    position: -webkit-sticky;
    position: sticky;
    top: 118px;
    z-index: 4;
}
</style>