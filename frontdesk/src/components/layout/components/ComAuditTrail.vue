<template>

 <InputText  placeholder="Search" @input="onSearch" />
 <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
 <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter" />
<div><ComOrderBy doctype="Comment" @onOrderBy="onOrderBy" /></div>

<DataTable :value="data" paginator :rows="5" :rowsPerPageOptions="[5, 10, 20, 50]" tableStyle="min-width: 50rem">
    <Column field="reference_doctype" header="Audit date"></Column>
    <Column field="reference_doctype" header=" Reference Type"></Column>
    <Column field="reference_name" header="Reference Name"></Column>
    <Column field="subject" header="Subject"></Column>
    <Column field="content" header="Description"></Column>
    <Column field="comment_by" header="Modified By"></Column>
    <Column field="creation" header="Date"></Column>
    <Column field="creation" header="Time"></Column>


</DataTable>

</template>

<script setup>

import { ref,inject,onMounted,getDocList } from '@/plugin';
const loading = ref(false);
const gv = inject("$gv")
const data = ref([])
function onLoadData(){
	loading.value = true
	getDocList('Comment', {	
		fields: ['reference_doctype','reference_name','subject','content','comment_by', "creation"],
	}).then((doc) => {
		data.value = doc
		loading.value = false			
	}).catch((rr)=>{
		gv.toast('error', rr)
	})
}
onMounted(() => {
	onLoadData()
})


</script>