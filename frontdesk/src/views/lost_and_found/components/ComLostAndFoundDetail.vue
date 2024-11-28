<template>
    <div class="grid">
        {{ data }}
    </div>
</template>
<script setup >
import { ref, inject, getDoc, getApi, onMounted } from '@/plugin';
const dialogRef = inject('dialogRef');
const loading = ref()
const data = ref({})
console.log(dialogRef.value.data.name)
function loadData() {
    loading.value = true
    getDoc("Lost and Found", dialogRef.value.data.name).then((r) => {
        data.value = r
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}
onMounted(() => {
    loadData()
});
</script>