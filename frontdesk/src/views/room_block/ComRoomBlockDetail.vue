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
        <!-- <Button  @click="onEditBlockRoom" >Edit</Button> -->
            <Button label="Edit " @click="visible = true" />
            <Button  @click="onUnBlockRoom">Unblock </Button> 
        </template>
    </ComDialogContent>
    <Dialog v-model:visible="visible" modal header="Edit Room Block Detail" :style="{ width: '50vw' }">
        <ComDialogContent @onClose="visible = false" @onOK="onSave">
            {{ data }}
        Block Date
        <div class="card flex justify-content-left">
            <Calendar v-model="data.block_date" />
        </div>
        Start Date
        <div class="card flex justify-content-left">
            <Calendar v-model="data.start_date" />
        </div>
        Release Date
        <div class="card flex justify-content-left">
            <Calendar v-model="data.end_date" showIcon />
        </div>
        Room Number
        <div class="card flex justify-content-left">
            <InputText type="text" v-model="data.room_number" />    
        </div>
            Room Type
        <div class="card flex justify-content-left">
            <InputText type="text" v-model="data.room_type" />    
        </div>
        Reason
        <div class="card flex justify-content-left">
            <Textarea v-model="data.reason" rows="5" cols="30" />
        </div>
    </ComDialogContent> 
    </Dialog>
</template>
<script setup>
import {ref,getDoc,onMounted,inject,useDialog, updateDoc } from "@/plugin"

const visible = ref(false);
const dialogRef = inject("dialogRef");
const doc = ref()
const loading = ref(false)
const gv = inject('$gv');
const dialog = useDialog()
const data = ref()

// db.getDoc('DocType', 'My DocType Name')
//   .then((doc) => console.log(doc))
//   .catch((error) => console.error(error));

// function onEditBlockRoom(){
// alert("hello")
// };

function onUnBlockRoom(){
    alert("How are you?");
}

function onCancel (){
    // alert("cancel")
}

function onSave (){
    loading.value = true
    updateDoc('Room Block', data.value.name, data.value).then((r)=>{
        doc.value = r
        doc.value.start_date = gv.dateFormat(r.start_date)
        doc.value.end_date = gv.dateFormat(r.end_date) 
        data.value = JSON.parse(JSON.stringify(r))
        loading.value = false
    })
}
onMounted(() => {
    loading.value = true
    getDoc("Room Block",dialogRef.value.data.name ).then((r)=>{
        doc.value = r
        doc.value.start_date = gv.dateFormat(r.start_date)
        doc.value.end_date = gv.dateFormat(r.end_date) 
        data.value = JSON.parse(JSON.stringify(r))
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
});

</script>