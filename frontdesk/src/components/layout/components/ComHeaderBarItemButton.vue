<template>
    <div :class="data.is_group ? 'menu-group wrapper-menu-bar_b' : 'wrapper-menu-bar_b'"> 
        <div class="progress-bar cursor-pointer text-center pt-2 pb-1 px-3 items-center text-white white-space-nowrap overflow-hidden text-overflow-ellipsis"
            :class="isCurrentPage ? 'active' : ''" @click="onClick(data.menu_name)">
            <div class="flex justify-center pb-1">
                <slot name="icon"></slot>
            </div>
            <div class="pro-navbar-txt">
                <slot name="defualt"></slot> 
            </div>
        </div>
        <div v-if="data?.is_group" class="sub-menu-1 bg-white">
            <ComHeaderBarItemChildButton :data="getChildMenu"/>
        </div>
    </div>
</template>
<script setup>
import { useRoute, computed,provide } from '@/plugin'
const current_page = computed(() => useRoute().name)
const emit = defineEmits(['onClick'])
const props = defineProps({
    data: Object
}) 
import { useScreen, useGrid } from 'vue-screen'
import ComHeaderBarItemChildButton from './ComHeaderBarItemChildButton.vue';
const screen = useScreen()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
// const items = ref(setting?.edoor_menu.filter(r => (r.parent_edoor_menu || "") == props.data.name))
const isCurrentPage = computed(()=>{
    if(current_page.value == props.data.menu_name){
        return 1
    }else{
        return 0
    }
})
const getChildMenu = computed(()=>{
    if(props.data.menu_text == 'Mores'){
        return setting.edoor_menu.filter(r=>r.parent_edoor_menu == props.data.name || (r.move_to_more && screen.width <= 1346))
    }
    return setting.edoor_menu.filter(r=>r.parent_edoor_menu == props.data.name)
})
function onClick(name){ 
    emit('onClick', name)
}
provide('on_header_menu',{
    onClick
})
</script>
<style scoped>
.menu-group .sub-menu-1{
    visibility: hidden;
    position: fixed;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    margin-top: 1px;
    width: min-content;
    min-width: 216px !important;
}
.menu-group:hover .sub-menu-1 {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-top: 2px solid var(--primary-border-color) !important;
    visibility: visible;
}
.sub-menu-text{
    white-space: nowrap;
}
</style>