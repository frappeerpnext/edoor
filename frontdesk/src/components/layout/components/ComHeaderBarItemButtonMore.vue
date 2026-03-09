<template>
    <ComHeaderBarItemButton @click="toggle">
        <template #icon>
            <img :src="iconEdoorMores">
        </template>
        <template #defualt>
            Mores
        </template>
    </ComHeaderBarItemButton>
</template>
<script setup>
import { ref } from '@/plugin'
import ComHeaderBarItemButton from './ComHeaderBarItemButton.vue';
import iconEdoorMores from '../../../assets/svg/icon-mores.svg'
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
function onLink(url) {
    window.open(serverUrl + '/app/' + url)
}
</script>