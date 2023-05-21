<template>
    <ComHeaderBarItemButton @click="toggle">
        <template #icon>
            <img :src="iconEdoorMores">
        </template>
        <template #defualt>
            Mores
        </template>
    </ComHeaderBarItemButton>
    <Menu ref="show" id="overlay_menu_more" :popup="true" style="min-width: 180px;">
        <template #end>
            <button @click="onLink('cashier-shift')"
                class="w-full flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <span class="ml-2">Chasier Report</span>
            </button>
            <button @click="onLink('sale/view/list')"
                class="w-full flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <span class="ml-2">Payout</span>
            </button>
            <button @click="onLink('expense/view/list')"
                class="w-full flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <span class="ml-2">Misc. Sale</span>
            </button>
        </template>
    </Menu>
</template>
<script setup>
import { ref } from 'vue'
import ComHeaderBarItemButton from './ComHeaderBarItemButton.vue';
import iconEdoorMores from '../../../assets/svg/icon-mores.svg'
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
function onLink(url) {
    window.open(serverUrl + '/app/' + url)
}
</script>