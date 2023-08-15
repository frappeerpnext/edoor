<template>
    <div :class="data.is_group ? 'menu-group wrapper-menu-bar_b' : 'wrapper-menu-bar_b'"> 
        <div class="progress-bar cursor-pointer text-center pt-2 pb-1 px-3 items-center text-white white-space-nowrap overflow-hidden text-overflow-ellipsis"
            :class="isCurrentPage ? 'active' : ''" @click="onClick(data.is_group,data.menu_name)">
            <div class="flex justify-center pb-1">
                <slot name="icon"></slot>
            </div>
            <div class="pro-navbar-txt">
                <slot name="defualt"></slot> 
            </div>
        </div>
        <div v-if="data?.is_group" class="sub-menu-1 bg-white">
            <template v-for="(item, index) in items.filter((item)=>item.hidden_in_lg == false || (item.hidden_in_lg == true && screen.width <= 1346))" :key="index">
                <button v-if="item.hidden_in_lg == false || (item.hidden_in_lg == true && screen.width <= 1346)" class="text-left py-2 px-3 hover:surface-200 w-full"
                    @click="onClick(item.is_group, item.menu_name)"
                    :class="[current_page == item.menu_name ? 'bg-gray-300' : '']">
                    <div class="flex gap-2">
                        <span v-if="item?.icon" v-html="item?.icon"></span>
                        <ComIcon v-else icon="iconGeneralList"></ComIcon> <span class="sub-menu-text">{{ item.menu_text }}</span>
                    </div>
                </button>
            </template>
        </div>
    </div>
</template>
<script setup>
import { useRoute, computed,ref } from '@/plugin'
const current_page = computed(() => useRoute().name)
const emit = defineEmits(['onClick'])
const props = defineProps({
    data: Object
}) 
import { useScreen, useGrid } from 'vue-screen'
const screen = useScreen()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const items = ref(setting?.edoor_menu.filter(r => (r.parent_edoor_menu || "") == props.data.name))
const isCurrentPage = computed(()=>{
    if(current_page.value == props.data.menu_name){
        return 1
    }else{
        return items.value.filter(r=>r.menu_name == current_page.value).length
    }
})

function onClick(isGroup,name){
    emit('onClick', name)
}
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