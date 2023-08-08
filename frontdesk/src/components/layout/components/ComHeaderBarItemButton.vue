<template>
    <div :class="data.is_group ? 'menu-group' : ''"> 
        <div class="progress-bar cursor-pointer text-center pt-2 pb-1 px-3 items-center text-white white-space-nowrap overflow-hidden text-overflow-ellipsis"
            :class="isCurrentPage ? 'active' : ''" @click="onClick(data.is_group,data.menu_name)">
            <div class="flex justify-center pb-1">
                <slot name="icon"></slot>
            </div>
            <div class="pro-navbar-txt">
                <slot name="defualt"></slot> 
            </div>
            
        </div>
        <div class="sub-menu-1 bg-white">
            <button class="text-left py-2 px-3 hover:surface-200 w-full" v-for="(item, index) in items" :key="index" @click="onClick(item.is_group, item.menu_name)"
                :class="[current_page == item.menu_name ? 'bg-gray-300' : '']"
                >
                {{ item.menu_text }}
            </button>
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
    position: absolute;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    margin-top: 1px;
}
.menu-group:hover .sub-menu-1 {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-top: 2px solid var(--primary-border-color) !important;
    visibility: visible;
    position: absolute;
    width: 13rem;
}

</style>