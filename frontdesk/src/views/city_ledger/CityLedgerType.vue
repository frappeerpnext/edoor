<template>
    <ComDocumentList
    doctype="City Ledger Type"
    list_view_setting="City_Ledger_Type"
    router_name="CityLedgerType"
    title="City Ledger Type" 
    :options="options"  
    >
    <template #action-button>
        <Button class="border-none" :label="isMobile ? $t('Add New') : $t('Add New City Ledger Account Type')" icon="pi pi-plus"  @click="onAddCityLedgerAccountType" />
    </template>

    <template #action="{ item }" >
                <div class="flex gap-2 justify-end">
                    <Button
                    @click="onEdit(item)"
                    icon="pi pi-pencil text-sm"
                    class="h-2rem border-none"
                    :label="$t('Edit')"
                    rounded
                    />
                    <Button
                    @click="onDelete(item.name)"
                    severity="danger"
                    icon="pi pi-trash text-sm"
                    class="h-2rem border-none"
                    :label="$t('Delete')"
                    rounded
                    />
                </div>
    </template>
    
    </ComDocumentList>
</template>

<script setup>
    import { ref,useDialog,inject,useConfirm,deleteDoc } from '@/plugin'
    import ComDocumentList from "@/components/document/ComDocumentList.vue";
    import ComAddCityLedgerType from "@/views/city_ledger/components/ComAddCityLedgerType.vue"
    import {i18n} from '@/i18n';

    const { t: $t } = i18n.global;
    const dialog = useDialog()
    const gv = inject("$gv")
    const isMobile = ref(window.isMobile) 
    const confirm = useConfirm()

    const options = ref({
        fields: [
            { fieldname: "name", is_hide:true},
            { fieldname: "name as city_ledger_type", label: "Name" },
            { fieldname: "note", label: "Note" },
            { fieldname: "modified", label: "Modified", fieldtype:"Datetime"},
            { fieldname: "modified_by", label: "Modified By" },
            { fieldname: "name as action", label: "Action", custom_class:"text-right" }
        ]
    })

    function onAddCityLedgerAccountType(){ 
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    dialog.open(ComAddCityLedgerType, {
        props: {
            header: $t(`Add New City Ledger Account Type`),
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose:(options) => {  
            const result = options.data;
            if (result) {  
                        window.postMessage({action:"ComDocumentList"},"*") 
            }
        }
    });  
}
 
function onEdit (edit){ 
    console.log("edit",edit);
    
 dialog.open(ComAddCityLedgerType, {
    props: {
        header: $t(`Edit City Ledger Type: ${edit.name}` ),
        style: {
            width: '50vw',
        },
        modal: true,
        closeOnEscape: false,
        position: 'top',
        breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
    },
    data:edit, 
    onClose:(options) => {
        const result = options.data;
        if(result){
            window.postMessage({action:"ComDocumentList"},"*") 
        }
    }
    
});  
}

function onDelete (name){ 
        confirm.require({
        message: 'Are you sure you want to delete guest?',
        header: $t('Confirmation'),
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            // loading.value = false
            deleteDoc('City Ledger Type',name)
            .then(() =>{
                window.postMessage({action:"ComDocumentList"},"*") 
                loading.value = false
            }).catch((err)=>{
                loading.value = false
            })         
        },
    });
}

</script>