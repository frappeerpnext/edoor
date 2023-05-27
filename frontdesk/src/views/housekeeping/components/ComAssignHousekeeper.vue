<template>
    <div>{{ data }}</div>
</template>
<script setup>
import { inject, onMounted , ref} from "vue";
const dialogRef = inject("dialogRef");
const data = ref()
 
onMounted(()=>{
    if(dialogRef){
        data.value = dialogRef.value.options.props.data
    }
})
</script>
