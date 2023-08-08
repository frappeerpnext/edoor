<template>
    <ComDialogContent @close="onClose" :loading="isSaving" hideButtonOK :hideButtonClose="true">
        <table>
            <tr>
                <td colspan="2" class="bg-slate-200 p-2 font-medium text-center border-1">Room Block</td>
            </tr>
            <ComStayInfoNoBox label="Block Number" v-if="doc?.name" :value="doc?.name"/>
            <ComStayInfoNoBox label="Room Number" v-if="doc?.room_number" :value="doc?.room_number"/>
            <ComStayInfoNoBox label="Room Type" v-if="doc?.room_type" :value="doc?.room_type"/>
            <ComStayInfoNoBox label="Start Date" v-if="doc?.start_date" :value="gv.dateFormat(doc?.start_date)"/>
            <ComStayInfoNoBox label="Release Date" v-if="doc?.end_date" :value=" gv.dateFormat(doc?.end_date)"/>
            <ComStayInfoNoBox label="Blocked by" v-if="doc?.modified_by" :value="doc?.modified_by"/>
            <ComStayInfoNoBox label="Block Date" v-if="doc?.modified" :value="gv.datetimeFormat(doc?.modified)"/>
        </table>
        <div class="w-full h-10rem mb-4 mt-2">
            <label>Reason</label>
            <div class="w-full p-3 h-10rem rounded-lg" style="background: rgb(243, 243, 243);">
                {{ doc?.reason }}
            </div>
        </div>
            
        <template #footer-right>

            <Button label="Edit" @click="onEdit" />
            <Button label="Unblock" @click="onUnblock" />

        </template>
    </ComDialogContent>
    <Dialog v-model:visible="unblockvisible" modal header="Edit Room Block Detail" :style="{ width: '50vw' }">
        <ComDialogContent @onClose="unblockvisible = false" @onOK="onSave()">
            Unblock Date
        <div class="card flex justify-content-left"> 
            <Calendar class="w-14rem" showIcon v-model="data.unblock_date" dateFormat="dd-mm-yy"/>
        </div><br>
        Housekeeping Status
        <div>
        <ComSelect  v-model="data.unblock_housekeeping_status" doctype="Housekeeping Status" />
        </div><br>
            Unblock Note
        <div class="card flex justify-content-left">
            <Textarea v-model="data.unblock_note" rows="5" cols="30" />
        </div>

    </ComDialogContent> 
    </Dialog>

</template>

<script setup>
import {ref,getDoc,onMounted,inject,useDialog, updateDoc } from "@/plugin"
import ComEditRoomBlock from "./components/ComEditRoomBlock.vue";
 
const unblockvisible = ref(false);

const dialogRef = inject("dialogRef");
const doc = ref()
const loading = ref(false)
const gv = inject('$gv');
const moment = inject('$moment');
const dialog = useDialog()
const data = ref()
const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))


function onEdit(){
    const dialogRef = dialog.open(ComEditRoomBlock, {
        data:doc.value,
        props: {
            header: 'Edit Room Block ' + doc.value.name,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false
        },
        onClose: (options) => {
            const result = options.data;
            if(result){
                data.value = result
            }
        }
    })
}
function onSave (){
    loading.value = true
    var savedData = {
        name: data.value.name,
        unblock_date: gv.dateApiFormat(data.value.unblock_date),
        unblock_housekeeping_status: data.value.unblock_housekeeping_status,
        unblock_note: data.value.unblock_note
    }
    updateDoc('Room Block', data.value.name, savedData).then((r)=>{
        dialogRef.value.close(r)
        loading.value = false
    })
}

function onUnblock(){
    data.value = JSON.parse(JSON.stringify(doc.value))
    unblockvisible.value = true
}

onMounted(() => {
    loading.value = true
    getDoc("Room Block",dialogRef.value.data.name ).then((r)=>{
        doc.value = r
        console.log(r)
        doc.value.start_date = gv.dateFormat(r.start_date)
        doc.value.end_date = gv.dateFormat(r.end_date)
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
});

</script>