<template>
    hello this is my map view teamplate 
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/83/Flag_of_Cambodia.svg"/>
    <br>
    {{ data }}
</template>
<script setup>
const props = defineProps({
    data: Object
})
</script>