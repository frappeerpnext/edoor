<template>
    <ComDialogContent hideButtonOK @onClose="onClose">
        <ComPlaceholder :loading="loading" :is-not-empty="true">
        <Timeline :value="data">
            <template #marker="slotProps">
                <div class="surface-ground w-2rem h-2rem border-circle h-full border-1" style="background: var(--bg-btn-dialog-inside);">
                    <span class="flex align-items-center justify-center h-full" v-if="slotProps?.item?.type == 'Version'">
                        <i class="pi pi-pencil"></i>
                    </span>
                    <span class="flex align-items-center justify-center h-full" v-else-if="slotProps?.item?.type == 'Frontdesk Note'">
                        <i class="pi pi-bookmark text-yellow-700"></i>
                    </span>
                    <span class="flex align-items-center justify-center h-full" v-else-if="slotProps?.item?.type == 'Comment'">
                        <i class="pi pi-upload" v-if="slotProps?.item?.comment_type == 'Attachment'"></i>
                        <i class="pi pi-comment" v-else-if="slotProps?.item?.comment_type == 'Comment'"></i>
                        <i class="pi pi-trash text-red-500" v-else-if="slotProps?.item?.comment_type == 'Attachment Removed' || slotProps?.item?.comment_type == 'Deleted Folio'"></i>
                    </span>
                    <span class="flex align-items-center justify-center h-full" v-else-if="slotProps?.item?.type == 'Folio Transaction'">
                        <i class="pi pi-dollar"></i>
                    </span>
                </div>
            </template>
            <template #content="slotProps">
                <div v-if="slotProps?.item?.type == 'Version'" class="mb-3 content">
                    <Button class="p-0 text-left" link @click="onDetail(slotProps.item)">
                        <div class="hover:underline text-gray-700" v-html="slotProps?.item?.description"></div>
                    </Button>
                    <div class="text-500">
                        <Timeago :long="true" :datetime="slotProps?.item?.creation" />
                        <ComNoticeAuditTrail v-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation'" :value="slotProps?.item?.docname"/>
                        <ComNoticeAuditTrail v-else-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation Stay'" :value="slotProps?.item?.docname"/>
                    </div>
                </div>
                <div v-else-if="slotProps?.item?.type == 'Comment'">
                    <div v-if="slotProps?.item?.comment_type == 'Comment'" style="background-color: var(--bg-comment);" class="cmmt-section mb-3 p-3 border-round-xl">
                        <div class="flex gap-3 mb-1">
                            <div>{{slotProps?.item?.owner == current_user ? 'You commented' : slotProps?.item?.owner}}</div>
                            <div class="text-500">
                                <Timeago :long="true" :datetime="slotProps?.item?.creation" />
                                <ComNoticeAuditTrail v-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation'" :value="slotProps?.item?.docname"/>
                                <ComNoticeAuditTrail v-else-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation Stay'" :value="slotProps?.item?.docname"/>
                            </div>
                        </div>
                        <div v-html="slotProps?.item?.content" class="content break-words"></div>
                    </div>
                    <div v-else-if="slotProps?.item?.comment_type == 'Deleted Folio'" class="mb-3">
                        <Button class="p-0 text-left" link @click="onDetail(slotProps.item)">
                            <div v-if="slotProps?.item && slotProps?.item?.content">
                                <span class="hover:underline text-gray-700">
                                    {{slotProps?.item?.owner == current_user ? 'You deleted' : slotProps?.item?.owner}} 
                                    <span class="lowercase">{{ slotProps.item?.doctype }}</span> on 
                                    Res. No: <strong>{{ slotProps?.item?.content.split('|')[0]}}, </strong>
                                    Res. Stay No: <strong>{{ slotProps?.item?.content.split('|')[1]}}, </strong>
                                    <span>
                                        <span v-if="slotProps?.item?.content.split('|')[2] === slotProps?.item?.content.split('|')[3]">folio number: <strong>{{ slotProps?.item?.content.split('|')[2]}}, </strong></span>
                                        <span v-else>folio number: <strong>{{slotProps?.item?.content.split('|')[3]}}, </strong></span>
                                    </span>
                                    Reason: <strong>{{ slotProps?.item?.content.split('|')[5]}}</strong>
                                </span>
                                
                            </div>
                        </Button>
                        <div class="text-500">
                            <Timeago :long="true" :datetime="slotProps?.item?.creation" />
                            <ComNoticeAuditTrail v-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Folio Transaction'" :value="slotProps?.item?.doctype"/>
                            <ComNoticeAuditTrail v-else-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation Stay'" :value="slotProps?.item?.docname"/>
                        </div>
                    </div>
                    <div v-else>
                        <div v-html="slotProps?.item?.content "></div>
                        <div class="text-500">
                            <Timeago :long="true" :datetime="slotProps?.item?.creation" />
                            <ComNoticeAuditTrail v-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation'" :value="slotProps?.item?.docname"/>
                            <ComNoticeAuditTrail v-else-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation Stay'" :value="slotProps?.item?.docname"/>
                        </div>
                    </div>
                </div>
                <div v-else-if="slotProps?.item?.type == 'Frontdesk Note'" class="ntd-section mb-3 p-3 border-round-xl" style="background-color: #faf6e9;">
                    <div class="">
                        <div class="flex gap-3 mb-1">
                            <div>{{slotProps?.item?.owner == current_user ? 'You noted' : slotProps?.item?.owner}}</div>
                            <div class="text-500">
                                <Timeago :long="true" :datetime="slotProps?.item?.creation" />
                                <ComNoticeAuditTrail v-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation'" :value="slotProps?.item?.docname"/>
                                <ComNoticeAuditTrail v-else-if="dialogRef.data?.doctype == 'Reservation' && slotProps?.item?.doctype == 'Reservation Stay'" :value="slotProps?.item?.docname"/>
                            </div>
                        </div>
                        <div v-html="slotProps?.item?.content" class="content break-words"></div>
                    </div>
                </div>
                <div class="mb-3" v-else>
                    <div class="flex gap-1">
                        <div>{{slotProps?.item?.owner == current_user ? 'You' : slotProps?.item?.owner}}</div>
                        <div v-html="slotProps?.item?.content" class="content break-words"></div>
                    </div>
                    <div class="text-500">
                        <Timeago :long="true" :datetime="slotProps?.item?.creation" />
                    </div>
                </div>
            </template>
        </Timeline>
    </ComPlaceholder>
    </ComDialogContent>
    <Dialog v-model:visible="visible" modal header="Audit Trail Detail" :style="{ width: '50vw' }">
        <ComAuditTrailDetail :data="selected" @onClose="onCloseDetail"/>
    </Dialog>
</template>
<script setup>
    import {getApi, inject,ref,onMounted, onUnmounted} from '@/plugin'
    import Enumerable from 'linq'
    import {Timeago} from 'vue2-timeago'
    import ComAuditTrailDetail from './ComAuditTrailDetail.vue';
    import ComNoticeAuditTrail from './ComNoticeAuditTrail.vue';
    const dialogRef = inject("dialogRef");
    const data = ref([])
    const loading = ref(true)
    const current_user = JSON.parse(localStorage.getItem('edoor_user')).name
    const visible = ref(false)
    const selected = ref({})
    onMounted(async () => {
        if(dialogRef.value.data){
            await onLoad(dialogRef.value?.data?.doctype, dialogRef.value?.data?.docname)
        }  
    })
    async function onLoad(doctype, docname){
        if(doctype && docname){
            loading.value = true
            await getApi('reservation.get_audit_trail',{
                doctype: doctype,
                docname: docname
            }).then((r)=>{
                data.value = Enumerable.from(r.message).orderByDescending("$.creation").toArray()
                loading.value = false
            }).catch((err)=>{
                loading.value = false
            })
        }
    }
    function onDetail(record){
        selected.value = record
        visible.value = true
    }
    
    function onCloseDetail(){
        visible.value = false
    }
    function onClose(){
        dialogRef.value.close()
    }
    onUnmounted(() => {
        data.value = []
    })


    // @media screen and (max-width: 960px) {
    //     ::v-deep(.customized-timeline) {
    //         .p-timeline-event:nth-child(even) {
    //             flex-direction: row !important;

    //             .p-timeline-event-content {
    //                 text-align: left !important;
    //             }
    //         }

    //         .p-timeline-event-opposite {
    //             flex: 0;
    //         }

    //         .p-card {
    //             margin-top: 1rem;
    //         }
    //     }
    // }
  
</script>
<style scoped>

.cmmt-section, .ntd-section{
    box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
}
</style>
