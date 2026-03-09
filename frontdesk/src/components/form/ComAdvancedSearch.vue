<template >
    <div>
        <div class="d-flex w-full">
            <span class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText class="w-full unrounded__box_cus bg-transparent" v-model="keyword" placeholder="Search" v-on:keyup.enter="onEnter"/>
            </span>
        </div>
        <div class="mt-4">

            <div class="relative overflow-x-auto">
                <table class="w-full text-left">
                    <thead class="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                            <th scope="col" class="px-3 py-3">
                                Name
                            </th>
                            <th scope="col" class="px-3 py-3">
                                Description
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="data.length > 0">
                            <tr v-for="(i, index) in data" :key="index" class="bg-white border-b">
                                <td scope="row" class="px-3 py-3 font-medium text-gray-900 whitespace-nowrap">
                                    <span class="cursor-pointer font-bold hover:underline" @click="onSelected(i[0])">{{ i[0] }}</span>
                                </td>
                                <td class="px-3 py-3">
                                    {{ i.join(', ') }}
                                </td>
                            </tr>
                        </template>
                        <template v-else>
                            <tr>
                                <td colspan="2">
                                    <div class="p-4 text-center">
                                        Empty
                                    </div>
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
<script setup>
import { inject, onMounted, ref } from 'vue'
const dialogRef = inject('dialogRef')
const frappe = inject('$frappe')
const call = frappe.call()
let keyword = ref('')
let doctype = ref('')
let data = ref([])
onMounted(() => {
    keyword.value = dialogRef.value?.options?.props?.keyword
    doctype.value = dialogRef.value?.options?.props?.doctype
    onSearch()
})
function onSearch() { 
    call.get('frappe.desk.search.search_widget', { doctype: doctype.value, txt: keyword.value }).then((result) => {
        data.value = result.values
    })
    .catch((error) => {
    }); 
}
function onEnter(){
    onSearch()
}
function onSelected(name){
    dialogRef.value.close(name)
}
</script>
<style ></style>