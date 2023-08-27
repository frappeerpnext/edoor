<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <h1>Old doc</h1>
        {{ doc }}
        <hr />
        <h1>New event</h1>
        {{ data }}

        <hr>
        <div class="flex align-items-center">
            <RadioButton v-model="generate_rate_type" inputId="regenerate_using_last_rate" name="regenerate" value="use_last_rate" />
            <label for="regenerate_using_last_rate" class="ml-2">Regenerate using first and Last stay date</label>
        </div>

        <div class="flex align-items-center">
            <RadioButton v-model="generate_rate_type" inputId="regenerate_rate_use_rate_plan" name="regenerate" value="use_rate_plan" />
            <label for="regenerate_rate_use_rate_plan" class="ml-2">Generate New Rate using Rate Plan</label>
        </div>

        <label>Note</label><br />
                <Textarea v-model="note" rows="3" placeholder="Note" cols="30"
                    class="w-full border-round-xl" />
       
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, getDoc,postApi } from "@/plugin"
const dialogRef = inject("dialogRef");
const data = ref({})
const doc = ref()
const isSaving =ref(false)
const generate_rate_type = ref("use_last_rate")
const note = ref("")
const moment = inject("$moment")
const socket = inject("$socket")


function onSave(){
    isSaving.value = true
    postApi("reservation.change_stay", 
        {
            data:{
                room_id: data.value.extendedProps.room_id,
                property: doc.value.property,
                room_type_id:data.value.extendedProps.room_type_id,
                start_date:moment(data.value.start).format("YYYY-MM-DD"),
                end_date:moment(data.value.end).format("YYYY-MM-DD"),
                parent:data.value.extendedProps.reservation_stay,
                generate_rate_type: generate_rate_type.value,
                note:note.value,
                name:data.value.id,
                ignore_check_room_occupy:1
            }
 }
    ).then((result)=>{
        isSaving.value = false
        dialogRef.value.close(result);
       
        socket.emit("RefresheDoorDashboard", doc.value.property);
        


    }).catch((err)=>{
        isSaving.value = false
    })
}
onMounted(() => {

    data.value = dialogRef.value.data;
    getDoc("Reservation Stay", data.value._def.extendedProps.reservation_stay).then((r) => {
        doc.value = r
    });




});
</script>