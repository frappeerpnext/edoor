<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Save" :hideIcon="false" :loading="loading">
        <DataTable :value="data?.fields" :reorderableColumns="true"   @rowReorder="onRowReorder" tableStyle="min-width: 50rem">
            <Column rowReorder headerStyle="width: 3rem" :reorderableColumn="false" />
            <Column  field="fieldname" header="Field Name" ></Column>
            <Column  field="label" header="Label" >
                <template #body="slotProps">
                    <InputText type="text" class="p-inputtext-sm w-full"  v-model="slotProps.data.label" :maxlength="50" />
                                       
                </template>
            </Column>
            <Column  field="action" header="Action" >
                <template #body="slotProps">
                    <InputText type="text" class="p-inputtext-sm w-full"  v-model="slotProps.data.action" :maxlength="50" />
                                       
                </template>
            </Column>
            
            <Column  field="id_field" header="ID Field" >
                <template #body="slotProps">
                    <InputText type="text" class="p-inputtext-sm w-full"  v-model="slotProps.data.id_field" :maxlength="50" />
                                       
                </template>
            </Column>

            
            <Column  field="is_hide" header="Hid in table" >
                <template #body="slotProps">
                    <Checkbox 
                                v-model="slotProps.data.is_hide" :binary="true" :trueValue="true" :falseValue="false" />
                                       
                </template>
            </Column>
            
            <Column header="" >
                <template #body="slotProps">
                <Button icon="pi pi-times" severity="danger" text rounded aria-label="Cancel"  @click="onRemoveField(slotProps.data)" />
                </template>
            </Column>

        </DataTable>

        <strong>Add new field</strong>
       
        <ComSelect :isFilter="true" v-if="meta" v-model="selectedField" :options="getOptionFields()" optionLabel="label"  placeholder="Select Field" />

        <Button label="Add Field" @click="onAddField"/>
        
    </ComDialogContent>


</template>
<script setup>
import { ref, inject, useDialog, createDocument, updateData,postData } from "@/plugin"
import { i18n } from '@/i18n';
import { onMounted } from "vue";
const { t: $t } = i18n.global;
import { useApp } from "@/hooks/useApp";
const dialog = useDialog();
const dialogRef = inject("dialogRef");
 
const {getMeta} = useApp()
const meta= ref()

const loading = ref(false)
const selectedField = ref()
 
const gv = inject("$gv")
 
 const data = ref()

function getOptionFields(){
    if(meta.value){

        let options = [
            {fieldname:"owner",fieldtype:"Data",label:"Owner"},
            {fieldname:"creation",fieldtype:"Date",label:"Creation"},
            {fieldname:"modified",fieldtype:"Date",label:"Modified"},
            {fieldname:"modified_by",fieldtype:"Data",label:"Modified By"},
        ]

        return options.concat(
            meta.value.fields.filter(r=>
                ['Data','Date','Datetime','Link','Currency','Float','Select'].includes(r.fieldtype) && 
                !data.value.fields.map(x=>x.fieldname).includes(r.fieldname)
        )
    )
    }
}

async function onOk() {
    loading.value = true;
    const res = await postData("edoor.edoor_configuration.doctype.app_list_view_setting.app_list_view_setting.SaveListViewSetting",
     {
        data:data.value
     }, "",true,"")

     loading.value = false

     if(res.data){
        res.data.fields = JSON.parse(res.data.fields)
        res.data.filter_options= JSON.parse(res.data.filter_options)
        dialogRef.value.close(res.data)
     }
}

function onAddField(){
   
    if (!selectedField.value){
        gv.toast("warn","Please select a field")
        return 

    }
    else {
        data.value.fields.push({
            fieldname:selectedField.value.fieldname,
            label:selectedField.value.label,
            fieldtype:selectedField.value.fieldtype

        })
    }
}

function onRemoveField(d){
    data.value.fields = data.value.fields.filter(r=>r.fieldname!=d.fieldname);
}

const onRowReorder = (event) => {
    data.value.fields = event.value;
    toast.add({severity:'success', summary: 'Rows Reordered', life: 3000});
};

onMounted(async() => {
data.value = dialogRef.value.data
   meta.value =  await getMeta(data.value.doctype)
})







</script>