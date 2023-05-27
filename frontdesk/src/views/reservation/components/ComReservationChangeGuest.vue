<template>
    <div>
        <div class="flex items-center">
            <div class="grow pr-2">
                <ComAutoComplete doctype="Customer" @onSelected="onSelected" isFull/>
            </div>
            <div class="flex-none">
                <div class="flex align-items-center">
                    <Checkbox v-model="isApplyAllStays" :binary="true" inputId="checkapplyall"/>
                    <label for="checkapplyall" class="ml-2"> Apply all stays</label>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
    import {ref, inject} from 'vue'
    const dialogRef = inject('dialogRef')
    const isApplyAllStays = ref(false)
    function onSelected(event){
        console.log(event)
        dialogRef.value.close(event)
    }
</script>
<style>
    .autocomplete-full-with input,
    .autocomplete-full-with{
        width: 100%;
        display: block;
    }
</style>