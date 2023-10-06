<template>
    <ComDialogContent @onClose="onClose" :loading="loading" hideButtonOK>
       
        <table>
            <tr>
                <td colspan="2" class="bg-slate-200 p-2 font-medium text-center border-1">Room Block</td>
            </tr>
            <ComStayInfoNoBox label="Block Number" v-if="doc?.name" :value="doc?.name"/>
            <ComStayInfoNoBox label="Room Name" v-if="doc?.room_number" :value="doc?.room_number"/>
            <ComStayInfoNoBox label="Room Type" v-if="doc?.room_type" :value="doc?.room_type"/>
            <ComStayInfoNoBox label="Start Date" v-if="doc?.start_date" :value="gv.dateFormat(doc?.start_date)"/>
            <ComStayInfoNoBox label="Release Date" v-if="doc?.end_date" :value="gv.dateFormat(doc?.end_date)"/>
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
            <Button class="border-none" icon="pi pi-pencil text-sm" label="Edit" @click="onEdit" />
            <Button class="border-none" icon="pi pi-lock-open text-sm" label="Unblock" @click="onUnblock" />
        </template>
    </ComDialogContent>
    <Dialog v-model:visible="unblockvisible" modal header="Edit Room Block Detail" :style="{ width: '50vw' }" position="top">
        <ComDialogContent @onClose="unblockvisible = false" @onOK="onSave()">
            <div class="grid">
                <div class="col-12 lg:col-6">
                    <label>Unblock Date</label>
                    <div class="card flex justify-content-left"> 
                        <Calendar selectOtherMonths class="w-full" showIcon v-model="data.unblock_date" dateFormat="dd-mm-yy"/>
                    </div>
                </div>
                <div class="col-12 lg:col-6">
                    <label>Housekeeping Status</label>
                    <div class="w-full">
                    <ComSelect class="w-full" v-model="data.unblock_housekeeping_status" doctype="Housekeeping Status" />
                    </div>
                </div>
                <div class="col-12">
                    <label>Unblock Note</label>
                    <div class="w-full card flex justify-content-left">
                        <Textarea class="w-full" v-model="data.unblock_note"  />
                    </div>
                </div>
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
// const moment = inject('$moment');
const dialog = useDialog()
const data = ref()
// const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))

function onEdit(){ 
    const dialogRef = dialog.open(ComEditRoomBlock, {
        data:doc.value,
        props: {
            header: 'Edit Room Block ' + doc.value.name,
            style: {
                width: '50vw',
            },
            modal: true,
            position:'top',
            closeOnEscape: false
        },
        onClose: (options) => {
            const result = options.data;
            if(result){
                doc.value = result
                gv.loading = false
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
        window.socket.emit("RefreshData", {property:data.value.property,action:"refresh_room_block"})
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
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
});

const onClose = () => {
    dialogRef.value.close()
}

</script>