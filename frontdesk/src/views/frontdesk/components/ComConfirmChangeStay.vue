<template>
{{ data }}
</template>
<script setup>
import {ref,onMounted,inject} from "@/plugin"
const dialogRef = inject("dialogRef");
const data = ref({})
onMounted(() => {
 
    data.value = dialogRef.value.data;
    

});
</script>