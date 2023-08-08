<template>
    <template v-for="(m, index) in eDoorMenu.filter(r => r.parent_edoor_menu == 'All Menus')" :key="index">
        <ComHeaderBarItemButton
            :data="m">
            <template #icon>
                <span v-html="m.icon"></span>
            </template>
            <template #defualt>
                <p>{{ m.menu_text }}</p>
            </template>
        </ComHeaderBarItemButton>
    </template>
</template>
<script setup>
import {onMounted,ref} from 'vue'
import ComHeaderBarItemButton from './ComHeaderBarItemButton.vue';
const eDoorMenu = ref([])
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
onMounted(() => {
    eDoorMenu.value = setting?.edoor_menu.filter(r => (r.parent_edoor_menu || "") != "")
})
</script>
<style lang="">
    
</style>