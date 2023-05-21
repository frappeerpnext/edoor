<template lang="">
    <div>
        {{bind}}
        <ComAutoComplete doctype="Customer" v-model="bind" isAddNew isAdvancedSearch @onSelected="onSelected" :filters="filters"/>
        <br/>
        {{bind}}
        <ComAutoComplete doctype="Customer" v-model="bind" isAddNew isAdvancedSearch/>
    </div>
</template>
<script setup>
    import {ref} from 'vue'
    let bind = ref('C2023-0108')
    const filters = '{"customer_group":"BABA"}'
    function onSelected(v){
        console.log(v)
    }
</script>
<style lang="">
    
</style>