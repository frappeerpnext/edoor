<template>
    <ComDialogContent @onClose="onClose" :loading="loading" hideButtonOK>
        {{ doc }}
       <Message v-if="doc?.docstatus==0">The status of this room block is currently in Draft mode. Please click on button <strong>Submit Room Block</strong> to block this room.
        <br/>
        <Button @click="onSubmitRoomBlock">Submit Room Block</Button>
       </Message>
       <Message v-if="doc?.docstatus==1 && doc?.is_unblock==0">This room number <strong>{{doc?.room_number}}</strong> is blocked now. To unblock this room, please on button <strong>Unblock</strong>
        <br/>
        <Button @click="onUnblock">Unblock this Room</Button>
       </Message>
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
            <div class="w-full p-3 h-10rem rounded-lg whitespace-pre-wrap break-words" v-html="doc?.reason">
               
            </div>
              </div>
            
        <template #footer-right>
            <Button v-if="doc?.docstatus==0" @click="onSubmitRoomBlock">Submit Room Block</Button>
            <Button v-if="!doc?.is_unblock" class="border-none" icon="pi pi-pencil text-sm" label="Edit" @click="onEdit" />
            <Button v-if="!doc?.is_unblock  && doc?.docstatus==1" class="border-none" icon="pi pi-lock-open text-sm" label="Unblock" @click="onUnblock" />
            <Button v-if="!doc?.is_unblock  && doc?.docstatus==0" class="border-none" icon="pi pi-trash text-sm" label="Delete" severity="danger"  @click="onDelete" />
        </template>
    </ComDialogContent>
    <Dialog v-model:visible="unblockvisible" modal header="Edit Room Block Detail" :style="{ width: '50vw' }" position="top">
        <ComDialogContent @onClose="unblockvisible = false" @onOK="onSave()" :loading="unblock_loading">
 
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
                      
                    <ComSelect placeholder="Housekeeping Status" class="w-full" v-model="data.unblock_housekeeping_status" :options="housekeepingStatus"
                    />
                    </div>
                </div>
                <div class="col-12">
                    <label>Unblock Note</label>
                    <div class="w-full card flex justify-content-left">
                        <Textarea class="w-full" v-model="data.unblock_note"  autoResize />
                    </div>
                </div>
            </div>
        </ComDialogContent> 
    </Dialog>
</template>

<script setup>
import {ref,getDoc,onMounted,inject,useDialog, updateDoc,useConfirm ,deleteDoc } from "@/plugin"
import ComEditRoomBlock from "./components/ComEditRoomBlock.vue";
const confirm = useConfirm()
const unblockvisible = ref(false);
const unblock_loading = ref(false);

const dialogRef = inject("dialogRef");
const doc = ref()
const loading = ref(false)
const gv = inject('$gv');
 
const dialog = useDialog()

const housekeepingStatus =ref( window.setting.housekeeping_status.filter(r=>r.is_room_occupy==0).map(r=>r.status)) ;



const data = ref()


function onSubmitRoomBlock(){
    confirm.require({
        message: 'Are you sure you want to block this room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            loading.value = true
            updateDoc("Room Block", doc.value.name ,{docstatus:1}).
            then(result=>{
               doc.value = result
               loading.value = false
               window.socket.emit("Frontdesk", window.property_name)
               window.socket.emit("ComHousekeepingStatus", window.property_name)
            }).catch(err=>{
                loading.value = false
            })
        },
        
    }); 
}

function onDelete(){
    confirm.require({
        message: 'Are you sure you want to delete this room block?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            loading.value = true
            deleteDoc("Room Block", doc.value.name).
            then(result=>{
            dialogRef.value.close()
               loading.value = false
               window.socket.emit("RoomBlockList",window.property_name)
               window.socket.emit("Frontdesk", window.property_name)
               window.socket.emit("ComHousekeepingStatus", window.property_name)

            }).catch(err=>{
                loading.value = false
            })
        },
        
    }); 
}
 
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
    unblock_loading.value = true
    var savedData = {
        name: data.value.name,
        unblock_date: gv.dateApiFormat(data.value.unblock_date),
        unblock_housekeeping_status: data.value.unblock_housekeeping_status,
        unblock_note: data.value.unblock_note,
        is_unblock:1
    }
    updateDoc('Room Block', data.value.name, savedData).then((r)=>{
        window.socket.emit("Frontdesk",window.property_name)
        window.socket.emit("RoomBlockList",window.property_name)
        window.socket.emit("Dashboard",window.property_name)
        window.socket.emit("ComHousekeepingStatus",window.property_name)
        doc.value = r
        unblockvisible.value =false
        unblock_loading.value = false
        
    }).catch((ex)=>{
        unblock_loading.value = false
    })
    
}

function onUnblock(){
    data.value = JSON.parse(JSON.stringify(doc.value))
    data.value.unblock_date = moment(data.unblock_date).toDate()
    data.value.unblock_housekeeping_status = housekeepingStatus.value[0]
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