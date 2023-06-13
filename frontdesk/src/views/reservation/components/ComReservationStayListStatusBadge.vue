<template>
    <div v-if="setting.reservation_status && lists.length > 0" class="flex flex-wrap gap-3"> 
        <div v-for="(i, index) in lists" :key="index">
            <!-- {{ i }} -->
            <div class="grow p-2 border-round-lg text-white border-none cursor-pointer" :style="[{ background: hexToRgbA(i.color, .3)}]">
                <div class="flex justify-center align-items-center h-full" :style="[{ color: i.color}]">
                    <div>
                        <div class="text-center white-space-nowrap">{{ i.name }} <span class="border-round-lg ml-1" style="padding:0 5px;color:#fff" :style="[{ background: hexToRgbA(i.color, .6)}]">{{ i.total }}</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import {inject, ref } from 'vue'
const setting = JSON.parse(localStorage.getItem('edoor_setting'))
const rs = inject('$reservation')
const lists = ref([]) 
if(setting && setting.reservation_status.length > 0 && rs && rs.reservation){
    setting.reservation_status.forEach(r => {
        let obj = {name: r.reservation_status, color: r.color, total: 0, sort: 0}
        if(r.reservation_status == 'Reserved'){
            obj.total = rs.reservation.reserved
            obj.sort = 1
            lists.value.push(obj)
        }
        else if(r.reservation_status == 'Checked In') {
            obj.total = rs.reservation.total_checked_in
            obj.sort = 2
            lists.value.push(obj)
        }
        else if(r.reservation_status == 'Checked Out') {
            obj.total = rs.reservation.total_checked_out
            obj.sort = 3
            lists.value.push(obj)
        }
        else if(r.reservation_status == 'No Show'){
            obj.total = rs.reservation.total_no_show
            obj.sort = 4
            lists.value.push(obj)
        }
        else if(r.reservation_status == 'Cancelled'){
            obj.total = rs.reservation.total_cancelled
            obj.sort = 5
            lists.value.push(obj)
        }
        
        else if(r.reservation_status == 'Void'){
            obj.total = rs.reservation.total_void
            obj.sort = 6
            lists.value.push(obj)
        }
    });

    lists.value.push({name: "Total Stay", color: "#000", total: rs.reservation.total_reservation_stay, sort:7})
    lists.value.push({name: "Total Active Stay", color: "#000", total: rs.reservation.total_active_reservation_stay, sort:8})
    lists.value = lists.value.sort((a, b) => (a.sort > b.sort) ? 1 : -1);

    
}

const hexToRgbA = (hex, alpha) => {
    let color;
    if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
        color= hex.substring(1).split('');
        if(color.length== 3){
            color= [color[0], color[0], color[1], color[1], color[2], color[2]];
        }
        color= '0x'+color.join('');
        return 'rgba('+[(color>>16)&255, (color>>8)&255, color&255].join(',')+','+alpha+')';
    }
    throw new Error('Bad Hex');
}

// console.log(hexToRgbA('#fbafff', .6))
    
 
</script>
