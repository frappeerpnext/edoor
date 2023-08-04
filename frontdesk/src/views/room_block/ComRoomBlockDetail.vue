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
        <div class="card flex justify-content-left">
        <Button label="Edit " @click="visible = true" />
        <Dialog v-model:visible="visible" modal header="Edit Room Block Detail" :style="{ width: '50vw' }">
            hello
            <div class="card flex justify-content-left">
                <span >
                    <InputText type="text" v-model="value" />
                </span>
                <div class="card flex justify-content-right">
                <span>
                    <InputText type="text" v-model="value" />
                </span>
            </div>     
    </div>
        </Dialog>
    </div>
    <Button  @click="onUnBlockRoom">Unblock </Button> 

    </template>
    </ComDialogContent>
</template>
<script setup>
import {ref,getDoc,onMounted,inject,useDialog } from "@/plugin"

const visible = ref(false);
const dialogRef = inject("dialogRef");
const doc = ref()
const loading = ref(false)
const gv = inject('$gv');
const dialog = useDialog()

 
// function onEditBlockRoom(){
// alert("hello")
// };
function onUnBlockRoom(){
    alert("How are you?");
}
onMounted(() => {
    loading.value = true
    getDoc("Room Block",dialogRef.value.data.name ).then((data)=>{
        doc.value= data;
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
  

});


</script>