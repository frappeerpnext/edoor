<template>
    hello this is my map view teamplate 
    <img :src="data.flag"/>
    <br>
    <div v-for="(c, index) in columns" :key="index">
        {{ c.fieldtype }}
        {{c.label}} : {{data[c.fieldname]}}
        <hr/>
    </div>
    <br>
    
</template>
<script setup>
const props = defineProps({
    data: Object,
    columns: Object,

})
</script>