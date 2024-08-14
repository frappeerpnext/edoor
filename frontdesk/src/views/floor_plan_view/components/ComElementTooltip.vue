<template>
    {{ bg }}
    <ColorPicker v-model="bg" />

    <hr>
    <Button>View Reservation Stay</Button>
</template>
<script setup>
import {ref} from "@/plugin"
import ColorPicker from 'primevue/colorpicker';
const props = defineProps({
    data:Object
})
const bg = ref("")
</script>