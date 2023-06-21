<template>
    <ComDialogContent hideButtonOK @onClose="onClose">
        <ComPlaceholder :loading="loading" :is-not-empty="true">
        <Timeline :value="data">
            <template #marker="slotProps">
                <div class="surface-ground w-2rem h-2rem flex align-items-center justify-center border-circle border-1" style="background: var(--bg-btn-dialog-inside);">
                    <span v-if="slotProps.item.type == 'Version'">
                        <i class="pi pi-pencil"></i>
                    </span>
                    <span v-else-if="slotProps.item.type == 'Frontdesk Note'">
                        <i class="pi pi-bookmark"></i>
                    </span>
                    <span v-else-if="slotProps.item.type == 'Comment'">
                        <i class="pi pi-upload" v-if="slotProps.item.comment_type == 'Attachment'"></i>
                        <i class="pi pi-comment" v-else-if="slotProps.item.comment_type == 'Comment'"></i>
                    </span>
                    
                </div>
            </template>
            <template #content="slotProps">
                <div v-if="slotProps.item.type == 'Version'" class="content">
                    <div>
                        <Button class="p-0 text-left" link @click="onDetail(slotProps.item)">
                            <div class="hover:underline text-gray-700" v-html="slotProps.item.description"></div>
                        </Button>
                    </div>
                    <small class="p-text-secondary">
                        <Timeago :long="true" :datetime="slotProps.item.creation" />
                    </small>
                </div>
                <div v-else>
                    <div class="flex gap-1">
                        <div>{{slotProps.item.owner == current_user ? 'You' : slotProps.item.owner}}</div>
                        <div v-html="slotProps.item.content" class="content break-words"></div>
                    </div>
                    <small class="p-text-secondary">
                        <Timeago :long="true" :datetime="slotProps.item.creation" />
                    </small>
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
    const dialogRef = inject("dialogRef");
    const data = ref([])
    const meta = ref([])
    const loading = ref(true)
    const current_user = JSON.parse(localStorage.getItem('edoor_user')).name
    const visible = ref(false)
    const selected = ref({})
    onMounted(async () => {
        if(dialogRef.value.data){
            await onGetMeta(dialogRef.value?.data?.doctype)
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
                const result = Enumerable.from(r.message).orderByDescending("$.creation").toArray()
                result.forEach((x)=>{
                    const prefix = x.owner == current_user ? 'You' : x.owner
                    if(x.type == 'Version'){
                        const content = JSON.parse(x.content)
                        if(content.added.length > 0){
                            let list = []
                            let description = ''
                            content.added.forEach((add)=>{
                                let pro_list = []
                                Object.entries(add[1]).forEach(([key, value]) => { 
                                    pro_list.push({property: key, value: value})
                                });
                                 
                                const property = getLabel(add[0])
                                description = description + property + ', '
                                list.push({property: property, value: pro_list}) 
                            })
                              
                            x['added'] = list
                            x['description'] = `${prefix} added rows for ${description.slice(0, -2)}`                
                        }
                        else if(content.changed.length > 0){
                            var pro_list = []
                            var description = ''
                            var count_result = 0
                            content.changed.forEach((c)=>{
                                const metakey = meta.value.fields.find((r)=>r.fieldname == c[0])
                                if(metakey.fieldtype != 'JSON' && metakey.fieldtype != 'Code' && metakey.fieldtype != 'HTML' && !metakey.hidden){
                                    count_result++
                                    var label = metakey?.label
                                    var original_value = c[1]//valueChangeFormat({value: c[1]})
                                    const new_value = c[2] //valueChangeFormat({value: c[2]})
                                    pro_list.push({
                                        property: label,
                                        original_value: original_value,
                                        new_value: new_value,
                                    })
                                    if(count_result <= 3){
                                        description = description + `${label} from  ${getText(original_value)} to ${getText(new_value)}, `
                                    }
                                } 
                            })
                            x['changed'] = pro_list,
                            x['description'] = `${ prefix } changed the value of ${description.slice(0, -2)}`
                        }
                        else if(content.row_changed.length > 0){
                            var list = []
                            content.row_changed.forEach((rh)=>{
                                var obj = {
                                    property: rh[0],
                                    index: rh[1],
                                    name: rh[2],
                                    feilds: rh[3],
                                }
                                list.push(obj)
                            })
                            var groups = Enumerable.from(list).groupBy(
                            "{property:$.property}",
                            "{index:$.index}",
                            "{property:$.property, index: $$.sum('$.index')}",
                            "$.property+','+$.index"
                            )
                            var group_list = []
                            const xx = Enumerable.from(groups).forEach(function(ii){
                                group_list.push({
                                    property: ii.property,
                                    rows: list.filter((l)=>ii.property == l.property)
                                })
                            })
                            groups.forEach((ii)=>{
                                group_list.push({
                                    property: ii.property,
                                    rows: list.filter((l)=>ii.property == l.property)
                                })
                            })
                            var description = `${prefix} changed the values for `
                            group_list.forEach((row)=>{
                                var label = meta.value.fields.find((r)=>r.fieldname == row.property)
                                description = description + `${label?.label} in row `
                                row.rows.forEach((rr)=>{
                                    description = description + `#${rr.index}, `
                                })
                                
                            })
                            x['row_changed'] = group_list
                            x['description'] = description.slice(0, -2)
                        }
                        else if(content.removed.length > 0){
                            var description = `${prefix} removed rows for `
                            var list = []
                            content.removed.forEach(rem => {
                                const label = getLabel(rem[0])//meta.value.fields.find((r)=>r.fieldname == rem[0])
                                description = description + label  + ', '
                                
                                let pro_list = []
                                Object.entries(rem[1]).forEach(([key, value]) => {
                                    pro_list.push({property: key, value: value})
                                }); 

                                list.push({
                                    property: label,
                                    options: getOption(rem[0]),
                                    value: pro_list
                                })
                            });
                            
                            x['removed'] = list
                            x['description'] = description.slice(0, -2)
                        }
                        data.value.push(x)
                        
                    }else{
                        data.value.push(x)
                    }
                })
                loading.value = false
            }).catch((err)=>{
                loading.value = false
            })
        }
    }
    async function onGetMeta(doctype){
        getApi('frontdesk.get_meta', {
            doctype: doctype
        }).then((r)=>{
            meta.value = r.message
        })
        
    }
    function onDetail(record){
        selected.value = record
        visible.value = true
    }
    function getLabel(key){ 
        console.log(meta.value.fields)
        if(key && meta.value && meta.value.fields && meta.value.fields.length > 0){
            const data = meta.value.fields.find((r)=>r.fieldname == key)
            if(data && data.label){
                return data.label
            }
        }
        return ''
    }
    function getText(txt){
        var text = stripHtmlTags(txt)
        text = text.slice(0,20) + (text.length> 20 ? '...' : '')
        return `<b>${text}</b>`
    }
    function stripHtmlTags(str)
    {
        if ((str===null) || (str==='')){
            return '""';
        }
        else{
            str = str.toString();
            return str.replace(/<[^>]*>/g, '');
        }
    
    }
    function getOption(key){
        if(key && meta.value && meta.value.fields && meta.value.fields.length > 0){
            const data = meta.value.fields.find((r)=>r.fieldname == key)
            if(data && data.options){
                return data.options
            }
        }
        return ''
    }
    function onCloseDetail(){
        visible.value = false
    }
    function onClose(){
        dialogRef.value.close()
    }
    onUnmounted(() => {
        meta.value = []
        data.value = []
    })
  
</script>
<style scoped>
@media screen and (max-width: 960px) {
    ::v-deep(.customized-timeline) {
        .p-timeline-event:nth-child(even) {
            flex-direction: row !important;

            .p-timeline-event-content {
                text-align: left !important;
            }
        }

        .p-timeline-event-opposite {
            flex: 0;
        }

        .p-card {
            margin-top: 1rem;
        }
    }
}
</style>