<template>
        <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Ok" :hideIcon="false" :loading="loading">
    
            <table class="w-full">
                <thead>
                <tr>
                    <td>Stay Date</td>
                    <td>Room Type</td>
                    <td>Room</td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(d, index) in data.stays" :key="index">
                    <td>{{ moment(d.start_date).format("DD-MM-YYYY") }} - {{ moment(d.end_date).format("DD-MM-YYYY") }}</td>
                    <td>         <Dropdown v-model="d.room_type_id" :options="d.room_types" optionValue="name"
                                     optionLabel="room_type" :placeholder="$t('Select Room Type')"
                                    class="w-full">
                                    <template #option="slotProps">
                                        <div class="flex align-items-center">

                                            <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room ||
                                                0 }})</div>
                                        </div>
                                    </template>
                                </Dropdown>
                            </td>
                    <td>
                        <Dropdown v-model="d.room_id"
                                    :options="d.rooms.filter((r) => (r.room_type_id == d.room_type_id && (r.selected ?? 0) == 0) || (r.room_type_id == d.room_type_id && r.name == d.room_id))"
                                    optionValue="name" @change="OnSelectRoom" optionLabel="room_number"
                                    :placeholder="$t('Select Room')" showClear filter class="w-full" />
         

                    </td>
                </tr>
            </tbody>
            </table>
            <hr class="mb-4 mt-4">
            <label for="reason-text" class="mb-1 font-medium block">Reason</label>
            <Textarea v-model="data.note" id="reason-text" rows="3" cols="50" placeholder="Please Enter Reason" class="w-full"/>

    </ComDialogContent>
</template>
<script setup>
    import {ref, getApi,postApi,onMounted,inject} from "@/plugin"
    import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
    const data = ref({note:""})
    const dialogRef = inject("dialogRef");
    const loading = ref(false)
    const moment = inject("$moment")
    function onOk(){
        loading.value = true
        postApi("reservation.reinstate",{
            data:{
                note:data.value.note,
                reservation:data.value.reservation,
                stays:[data.value.reservation_stay],
                stay_rooms:data.value.stays.map(r=>({
                    name:r.name,
                    room_type_id:r.room_type_id,
                    room_id:r.room_id
                })),
                property:data.value.property
            }
        })
        .then(r=>{
            loading.value = false
            dialogRef.value.close(true)
        }).catch(error=>{
            loading.value = false
        })
    }
    
    onMounted(()=>{
        data.value = dialogRef.value.data
        loading.value = true
        postApi("reservation.get_check_reinstate_reservation",{
            data:{
                reservation:data.value.reservation,
                reservation_stay:data.value.reservation_stay,
                property:data.value.property,
                
            }
        },"",false)
        .then(r=>{
            loading.value = false
            data.value = r.message
        }).catch(error=>{
            loading.value = false
        })

    })


    
</script>