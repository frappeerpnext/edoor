<template>
   <ComDialogContent hideButtonOK :hideButtonClose="false" @onClose="onClose" :loading="loading">
        <div class="iframe-view guest-detail">
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium flex justify-content-center">
                <div class="flex align-items-center">
{{ data?.room_type }}
                </div>
            </div>
            <table>
                
                <ComStayInfoNoBox label="Room Type Group" :value="data?.room_type_group" />
                <ComStayInfoNoBox label="Room Name" :value="data?.room_number" />
                <ComStayInfoNoBox label="Status" >
                    <div class="flex font-semibold" style="margin-left: -10px;">

                        <span :style="{color:data.status_color}" >
                    {{ data?.housekeeping_status }}
                    </span>
                    </div>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Housekeeper" :value="data?.housekeeper" />
            </table>
           
            <hr class="my-3">
            <div class="my-3 line-height-2 ">
            <div class="mt-auto text-sm flex justify-content-end">
                    <span class="italic me-1">Created by : </span>
                    <span class="text-500 font-italic">
                        {{ data && data.owner && typeof data.owner === 'string' ? data.owner.split('@')[0] : '' }}
                        <ComTimeago :date="data?.creation"/>                      
                    </span>
                </div>
                <div class="mt-auto text-sm flex justify-content-end">
                    <span class="italic me-1"> Last Modified : </span>
                    <span class="text-500 font-italic">
                        {{ data && data.modified_by && typeof data.modified_by === 'string' ? data.modified_by.split('@')[0] : '' }}
               
                        <ComTimeago :date="data?.modified" />
                         
                    </span>
                </div>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted ,getDoc} from '@/plugin'
const gv = inject('$gv');
const dialogRef = inject("dialogRef")
const name = ref("")
const data = ref("");
function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|' + name, '*')
}
const onClose = () => {
    dialogRef.value.close()
}
function onViewReservationStayDetail(rs) {
    window.postMessage('view_reservation_stay_detail|' + rs, '*')

}

function onViewReservationDetail(rs) {
    window.postMessage('view_reservation_detail|' + rs, '*')
}
onMounted(() => {
    name.value = dialogRef.value.data.name
    getDoc("Room", dialogRef.value.data.name).then((r) => {
        data.value = r
        loading.value = false
    })
})
</script>
