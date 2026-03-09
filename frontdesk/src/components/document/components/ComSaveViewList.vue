<template>


    <ComRepeatView ref="repeatView" classList="flex flex-col gap-2" v-model:items="items" 
    doctype="List Filter" :options="{
        fields: ['name', 'filter_name', 'for_user', 'custom_view_filters'],
        filters: [['reference_doctype', '=', doctype],['custom_list_view_setting','=',list_view_setting]]
    }">
        
        <template #default="{ item, index }"> 
            <div class="relative">
                <Button :class="item.name==activeItemId?isActive:''" class="w-full border-0 text-left saved_filter_button"
                    style="height:30px !important; background: rgb(130 130 130 / 24%);color:#495057;"
                    :label="item.filter_name" @click="onOpenView(item)">
                </Button>
                <div class="absolute" style="right:-2px;top:50%;transform: translateY(-50%);">
                    <!-- <i class="pi pi-times"></i> -->
                    <Button @click="clearFilterView(item)" icon="pi pi-times" aria-label="Submit" class="border-none bg-transparent align-items-center flex" style="color:rgb(130 130 130);" iconClass="text-sm mt-1"/>
                </div>
            </div>
        </template>
    </ComRepeatView>
    
</template>
<script setup>
import { useRouter, ref, computed, deleteDocument,useConfirm } from "@/plugin"  
import { onMounted } from "vue"
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const router = useRouter() 
const activeItemId = ref(null) 
const confirm = useConfirm()
const props = defineProps({
    doctype: String,
    options: Object,
    router_name: String,
    list_view_setting:String
})
const items = defineModel([])
const repeatView = ref(null)
defineExpose({
    reloadData 
})
function reloadData(){
   
    repeatView.value.loadData();

   
}

 
function onOpenView(v) {
    localStorage.setItem('saved_filter_name', v.name)
    activeItemId.value = v.name
    router.push({ name: props.router_name, hash: "#" + v.name })
}

const isActive = computed(() => {
    return 'active_saved_filter'
})

const clearFilterView = (item) => {
    confirm.require({
        message: $t('Are you sure you want to clear filter?'),
        header: $t('Confirmation'),
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: $t('Ok'),
        accept: () => {
            const res = deleteDocument("List Filter", item.name, {
                hide_error_message: true
            })
            localStorage.removeItem('saved_filter_name')
            window.location.reload()
        }
    })
}
 
onMounted(() => {
    activeItemId.value = localStorage.getItem('saved_filter_name')
})
</script>
<style>
    .saved_filter_button .p-button-label {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 235px;
        display: inline-block;
    }
    .active_saved_filter {
        background: rgba(99, 102, 241, 0.24) !important;
        color: #6366f1 !important;
    }
</style>