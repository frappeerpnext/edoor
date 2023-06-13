<template>
    <ComDialogContent hideButtonOK @onClose="onClose">
        <ComPlaceholder :loading="loading" :is-not-empty="true">
            {{ data.length }}
            <div v-for="(i, index) in data" :key="index" class="border border-blue-500 p-4 mb-2">
                <div><b>{{ i.type }}</b> /{{ i.owner }} / {{ i.comment_type }} / <Timeago :long="true" :datetime="i.creation" /></div>
                <div v-if="i.type == 'Version'" class="content">
                    <div>
                        <Button class="p-0" link @click="onDetail(i)">
                            <div class="hover:underline text-gray-700" v-html="i.description"></div>
                        </Button>
                    </div>
                </div>
                <div  v-else>
                    <div v-html="i.content" class="content break-words"></div>
                </div>
            </div>
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
                                count_result++
                                if(c[0] != 'keyword'){
                                    var label = meta.value.fields.find((r)=>r.fieldname == c[0]) //getLabel(c[0])
                                    label = label?.label
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
<style lang="">
    
</style>