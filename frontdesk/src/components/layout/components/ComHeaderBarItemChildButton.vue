<template>
    <!-- {{ isCurrentPage }} -->
    <template v-for="(item, index) in data" :key="index">
        <button class="text-left py-2 px-3 hover:surface-200 w-full"
            @click="onClick(item.menu_name)"
            :class="[current_page == item.menu_name ? 'bg-gray-300' : '']">
            <div class="flex gap-2">
                <span v-if="item?.sub_menu_icon" v-html="item?.sub_menu_icon"></span>
                <ComIcon v-else icon="iconGeneralList"></ComIcon> <span class="sub-menu-text white-space-nowrap">{{ item.menu_text }}</span>
            </div> 
       </button>
       <template v-if="setting.edoor_menu.filter(r=>r.parent_edoor_menu == item.name).length > 0">
            <button v-for="(child, index) in setting.edoor_menu.filter(r=>r.parent_edoor_menu == item.name)" :key="index" class="text-left py-2 px-4 hover:surface-200 w-full"
                @click="onClick(child.menu_name)"
                :class="[current_page == child.menu_name ? 'bg-gray-300' : '']">
                <div class="flex gap-2 ml-3">
                    <span v-if="child?.sub_menu_icon" v-html="child?.sub_menu_icon"></span>
                    <ComIcon v-else icon="iconGeneralList"></ComIcon> <span class="sub-menu-text white-space-nowrap">{{ child.menu_text }}</span>
                </div> 
            </button>
       </template> 
    </template>
</template>
<script setup>
    import { useRoute,computed,inject } from '@/plugin'
    const props = defineProps({
        data: Array,
        parent: {
            type: String,
            default: null
        }
    })
    const {onClick} = inject('on_header_menu')
    const setting = JSON.parse(localStorage.getItem("edoor_setting"))
    const current_page = computed(() => useRoute().name)
    const isCurrentPage = computed(()=>{
        if(current_page.value == props.data.menu_name){
            return 1
        }else{
            return setting.value.edoor_menu.filter(r=>r.menu_name == current_page.value).length
        }
    })
</script>
<style lang="">
    
</style>