<template>
    <ComDialogContent @onClose="onClose" :loading="loading" hideButtonOK>
        <div v-if="doc?.docstatus == 0"
            class="  bg-orange-200 border-orange-500 p-2 font-medium border-left-3 mb-3 w-full flex align-items-center"> <i
                class="pi pi-file-edit me-2 text-lg" /> Draft</div>
        <div v-if="doc?.is_unblock != 0"
            class="surface-200 border-left-3 border-400 p-1px px-2  p-2 flex align-items-center"> <i
                class="pi pi-lock-open me-2 text-lg" /> Unblock </div>
        <div v-if="doc?.docstatus == 1 && doc?.is_unblock == 0"
            class="surface-200 border-left-3 border-black-alpha-90 p-2 p-1px px-2 flex align-items-center"> <i
                class="pi pi-lock me-2 text-lg" /> Block </div>
        <div class="ms_message_cs_edoor">
            <Message class="w-full" :closable="false" v-if="doc?.docstatus == 0">
                <div class="grid">
                <div class="col-12 md:col-8">
                    The status of this room block is currently in Draft mode. Please click on button
                    <strong>Submit Room Block</strong> to block this room.
                </div>
                <Button class="border-none me-3 ml-auto col" @click="onSubmitRoomBlock">
                    <i class="pi pi-send me-3" />
                    Submit Room Block</Button>
                </div>
            </Message>
            <Message class="w-full" :closable="false" v-if="doc?.docstatus == 1 && doc?.is_unblock == 0">
<div class="grid w-full">
                <div class="col-12 md:col-8">
                    This room number <strong>{{ doc?.room_number }}</strong> is blocked now. To unblock this room, please on
                    button <strong>Unblock</strong>
                </div>
                <div class="col-12 md:col flex justify-content-end">
                <Button class="border-none me-3 ml-auto" @click="onUnblock"> <i class="pi pi-lock-open me-3" /> Unblock this
                    Room</Button>
                    </div>
</div>
            </Message>
        </div>
        <div v-if="doc && doc?.is_unblock != 0">
            <div class="bg-slate-200 p-2 mt-4 font-medium text-center border-left-2">
                UnBlock
            </div>
            <table>
                <ComStayInfoNoBox label="Unblock Date" v-if="doc.unblock_date" :value="gv.dateFormat(doc.unblock_date)" />
                <ComStayInfoNoBox label="Unblock Housekeeping Status" v-if="doc.unblock_housekeeping_status_code"
                    :value="doc.unblock_housekeeping_status_code" />
            </table>
            <div class="w-full h-10rem mb-4 mt-2">
                <label>Reason</label>
                <div class="w-full p-3 h-10rem rounded-lg whitespace-pre-wrap break-words bg-slate-200"
                    v-html="doc.unblock_note"></div>
            </div>
            <hr class="my-4">
        </div>

        <div class="bg-slate-200 p-2 font-medium text-center border-left-2 mt-4">
            Room Block
        </div>
        <table>
            <ComStayInfoNoBox label="Block Number" v-if="doc?.name" :value="doc?.name" />
            <ComStayInfoNoBox label="Room Name" v-if="doc?.room_number" :value="doc?.room_number" />
            <ComStayInfoNoBox label="Room Type" v-if="doc?.room_type" :value="doc?.room_type" />
            <ComStayInfoNoBox label="Block Date" v-if="doc?.modified" :value="gv.dateFormat(doc?.block_date)" />
            <ComStayInfoNoBox label="Start Date" v-if="doc?.start_date" :value="gv.dateFormat(doc?.start_date)" />
            <ComStayInfoNoBox label="Release Date" v-if="doc?.end_date" :value="gv.dateFormat(doc?.end_date)" />
            <ComStayInfoNoBox label="Total Night(s)" v-if="doc?.total_night_count" :value="doc?.total_night_count" />
            <ComStayInfoNoBox label="Blocked by" v-if="doc?.modified_by" :value="doc?.modified_by?.split('@')[0]" />
        </table>
        <div class="w-full h-10rem mb-4 mt-2">
            <label>Reason</label>
            <div class="w-full p-3 h-10rem rounded-lg whitespace-pre-wrap break-words bg-slate-200" v-html="doc?.reason">
            </div>
        </div>
        <div class="col-12 p-0 pt-2">
            <ComCommentAndNotice v-if="doc?.name" doctype="Room Block" :docname="doc?.name"
                :filters="['custom_room_block', '=', doc.name]" />
        </div>
        <template #footer-right>
            <Button v-if="doc?.docstatus == 0" @click="onSubmitRoomBlock" class="border-0"> <i class="pi pi-send me-3" />
                Submit Room Block</Button>
            <Button v-if="!doc?.is_unblock" class="border-none" icon="pi pi-pencil text-sm" label="Edit" @click="onEdit" />
            <Button v-if="!doc?.is_unblock && doc?.docstatus == 1" class="border-none" icon="pi pi-lock-open text-sm"
                label="Unblock" @click="onUnblock" />
            <Button v-if="!doc?.is_unblock && doc?.docstatus == 0" class="border-none" icon="pi pi-trash text-sm"
                label="Delete" severity="danger" @click="onDelete" />
        </template>
        <template #footer-left>
            <Button class="border-none" @click="onAuditTrail" label="Audit Trail" icon="pi pi-history" />
            <!-- <Button class="border-none" @click="onPrintFolioTransaction" label="Print" icon="pi pi-print" /> -->
        </template>
    </ComDialogContent>
    <Dialog v-model:visible="unblockvisible" modal header="Edit Room Block Detail" :style="{ width: '50vw' }"
        position="top">
        <ComDialogContent @onClose="unblockvisible = false" @onOK="onSave()" :loading="unblock_loading">
            <div class="grid">
                <div class="col-12 lg:col-6">
                    <label>Unblock Date </label>
                    <div class="card flex justify-content-left">
                        <Calendar selectOtherMonths class="w-full" showIcon v-model="data.unblock_date"
                            dateFormat="dd-mm-yy" />
                    </div>
                </div>
                <div class="col-12 lg:col-6">
                    <label>Housekeeping Status</label>
                    <div class="w-full">
                        <ComSelect placeholder="Housekeeping Status" class="w-full" optionLabel="status"
                            optionValue="status" v-model="data.unblock_housekeeping_status_code"
                            :options="housekeeping_status_code" />
                    </div>
                </div>
                <div class="col-12">
                    <label>Unblock Note</label>
                    <div class="w-full card flex justify-content-left">
                        <Textarea class="w-full" v-model="data.unblock_note" autoResize />
                    </div>
                </div>
            </div>
        </ComDialogContent>
    </Dialog>
</template>
<script setup>
import { ref, getDoc, onMounted, inject, useDialog, updateDoc, useConfirm, deleteDoc } from "@/plugin"
import ComEditRoomBlock from "./components/ComEditRoomBlock.vue";
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
const confirm = useConfirm()
const unblockvisible = ref(false);
const unblock_loading = ref(false);
const dialogRef = inject("dialogRef");
const doc = ref()
const loading = ref(false)
const gv = inject('$gv');
const dialog = useDialog()
const housekeeping_status_code = ref(window.setting.housekeeping_status_code);
const data = ref()
const isMobile = ref(window.isMobile) 
function Refresh() {
    pageState.value.page = 0
    loadData()
}

function onSubmitRoomBlock() {
    confirm.require({
        message: 'Are you sure you want to block this room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            updateDoc("Room Block", doc.value.name, { docstatus: 1 }).
                then(result => {
                    doc.value = result
                    loading.value = false
                    window.postMessage({"action":"ComHousekeepingStatus"},"*")
                    window.postMessage({"action":"RoomBlockList"},"*")
                }).catch(err => {
                    loading.value = false
                })
        },

    });
}

function onDelete() {
    confirm.require({
        message: 'Are you sure you want to delete this room block?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            deleteDoc("Room Block", doc.value.name).
                then(result => {
                    dialogRef.value.close()
                    loading.value = false
                    window.postMessage({"action":"RoomBlockList"},"*")                    
                    window.postMessage({"action":"ComHousekeepingStatus"},"*")

                }).catch(err => {
                    loading.value = false
                })
        },

    });
}

function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Room Block',
            docname: doc?.value.name,
            referenceTypes: [{ doctype: 'Room Block', label: 'Room Block' }],
            filter_key: "custom_room_block",
        },

        props: {
            header: 'Audit Trail for Room Block',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
        },
        onClose: (options) => {
            // Handle dialog closure here
        },
    });
}

function onEdit() {
    const dialogRef = dialog.open(ComEditRoomBlock, {
        data: doc.value,
        props: {
            header: 'Edit Room Block ' + doc.value.name,
            style: {
                width: '50vw',
            },
            modal: true,
            position: 'top',
            closeOnEscape: false
        },
        onClose: (options) => {
            const result = options.data;
            if (result) {
                doc.value = result
                gv.loading = false
            }
        }
    })

}

function onSave() {
    unblock_loading.value = true
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
        window.socket.emit("ComHousekeepingRoomDetailPanel", { property: window.property_name })
        doc.value = r
        unblockvisible.value = false
        unblock_loading.value = false

    }).catch((ex) => {
        unblock_loading.value = false
    })

}
function loadData() {
    loading.value = true
    loading.value = true
    getDoc("Room Block", dialogRef.value.data.name).then((r) => {
        doc.value = r
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}

function onUnblock() {
    data.value = JSON.parse(JSON.stringify(doc.value))
    data.value.unblock_date = moment(data.unblock_date).toDate()
    data.value.unblock_housekeeping_status_code = housekeeping_status_code.value[0].status
    unblockvisible.value = true
}

onMounted(() => {
    loadData()
    if(window.isMobile){
    const elem = document.querySelector(".p-dialog");
		elem?.classList.add("p-dialog-maximized"); // adds the maximized class

 }
});

const onClose = () => {
    dialogRef.value.close()
}

</script>