<template>
       <ComDialogContent  @onOK="onSave()" @onClose="onClose" :loading="loading">
            <div class="grid">
                <div class="col-12 lg:col-6">
                    <label> {{ $t('Unblock Date') }}  </label>
                    <div class="card flex justify-content-left">
                        <Calendar selectOtherMonths class="w-full" showIcon v-model="data.unblock_date"
                            dateFormat="dd-mm-yy" />
                    </div>
                </div>
                <div class="col-12 lg:col-6">
                    <label> {{ $t('Housekeeping Status') }} </label>
                    <div class="w-full">
                        <ComSelect placeholder="Housekeeping Status" class="w-full" optionLabel="status"
                            optionValue="status" v-model="data.unblock_housekeeping_status_code"
                            :options="housekeeping_status_code" />
                    </div>
                </div>
                <div class="col-12">
                    <label> {{ $t('Unblock Note') }} </label>
                    <div class="w-full card flex justify-content-left">
                        <Textarea class="w-full" v-model="data.unblock_note" autoResize />
                    </div>
                </div>
            </div>
        </ComDialogContent>

</template>
<script setup>
import {ref, inject, onMounted,updateDoc} from "@/plugin"
const dialogRef = inject('dialogRef');
const data = ref({})
const gv  = inject("$gv")
const housekeeping_status_code = ref(window.setting.housekeeping_status_code);
const loading = ref(false)

function onSave(){
    loading.value = true
    const savedData = {
        name: data.value.name,
        unblock_date: gv.dateApiFormat(data.value.unblock_date),
        unblock_housekeeping_status_code: data.value.unblock_housekeeping_status_code,
        unblock_note: data.value.unblock_note,
        is_unblock: 1
    }
    updateDoc('Room Block', data.value.name, savedData).then((r) => {
        window.postMessage({"action":"RoomBlockList"},"*")        
        window.postMessage({"action":"Dashboard"},"*")
        window.postMessage({"action":"ComHousekeepingStatus"},"*")
        window.postMessage({action:"Housekeeping"},"*")
        window.postMessage({action:"FloorPlanView"},"*")

        loading.value = false
        dialogRef.value.close(r)

    }).catch((ex) => {
        loading.value = false
    })

}
function onClose(){
    dialogRef.value.close()
}

onMounted(()=>{
    data.value  = dialogRef.value.data

})
</script>