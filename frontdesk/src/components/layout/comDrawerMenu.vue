<template>
    <Button icon="pi pi-bars" style="background: transparent" class="border-none" @click="visible = true" />
    <div class="wrapper-sidebar"> 
        <Sidebar v-model:visible="visible" id="sbar"> 
            <template #header>
                <div>
                    <div class="profile bg-primary w-4rem h-4rem border-circle overflow-hidden">
                        <img class="image-profile w-full h-full" style="object-fit: cover;" :src="user.photo"/>
                    </div>
                    <h1 class="text-2xl font-semibold pt-3">{{user.full_name}}</h1>
                    <p>rathanachamroeun155@gmail.com</p>
                </div>
            </template>
            <div class="pt-3"> 
                <template v-for="(item, index) in items" :key="index">
                    <div v-if="!item.items" class="wrapper-nav-hover">
                        <a v-ripple @click="onNavigate(item)">
                            <span :class="index == 0 ? 'ml-1' : ''" class="flex align-items-center gap-2 w-full" style="padding-top:1.25rem; padding-bottom:1.25rem">
                                <span v-html="item.icon"></span>
                                <span class="font-bold text-white white-space-nowrap">{{ item.label }}</span> 
                            </span>
                        </a>
                    </div>
                    <div v-else class="wrapper-drop-sm">
                        <Accordion>
                            <AccordionTab>
                                <template #header>
                                    <span class="flex align-items-center gap-2 w-full">
                                        <span v-html="item.icon"></span>
                                        <span class="font-bold white-space-nowrap">{{ item.label }}</span>
                                    </span>
                                </template> 
                                <template v-for="(sub_item, index) in item.items" :key="index">
                                    <div class="wrapper-nav-hover">
                                        <a v-ripple @click="onNavigate(sub_item)">
                                            <span class="flex align-items-center gap-2 w-full" style="padding-top:1.25rem; padding-bottom:1.25rem;margin-left:15px">
                                                <ComIcon icon="iconGeneralList"></ComIcon>
                                                <span class="font-bold text-white white-space-nowrap">{{ sub_item.label }}</span> 
                                            </span>
                                        </a>
                                    </div>
                                </template>
                            </AccordionTab> 
                        </Accordion> 
                    </div>
                </template>  
            </div>
        </Sidebar>
    </div>
</template>
<script setup>
import { ref, computed, useRouter, onMounted } from "@/plugin"

const props = defineProps({
    user: Object
})

const router = useRouter();
const visible = ref(false)
const eDoorMenu = computed(() => {

    const menu = ref(setting?.edoor_menu.filter(r => (r.parent_edoor_menu || "") != ""))


    return menu.value

})



const items = ref([])

function onNavigate(menu) {
    visible.value = false
    router.push({ name: menu.route }) 
  
}
onMounted(() => {
    items.value = []
    eDoorMenu.value.filter(r => r.parent_edoor_menu == "All Menus").forEach(p => {
        let menu_item = { label: p.menu_name == "Mores" ? "Other" : p.menu_text, icon: p.icon, route: p.menu_name }
        const sub_menu = eDoorMenu.value.filter(x => x.parent_edoor_menu == p.name)
        if (sub_menu.length > 0) {
            menu_item.items = []
            if (p.menu_name != "Mores") {
                menu_item.items.push({ label: p.menu_name == "Mores" ? "Other" : p.menu_text, icon: p.icon, route: p.menu_name })
            }
            sub_menu.forEach(s => {
                menu_item.items.push({ label: s.menu_text, icon: s.icon, route: s.menu_name })
            })
        }
        items.value.push(menu_item)
    });
})
</script>
<style>
#sbar .p-sidebar-content{
    position: relative;
    z-index: 1;
    background: #204887;
}
#sbar{
    overflow: hidden;
    background: #204887;
}
#sbar .p-sidebar-header{ 
    margin-bottom: 24px;
    display: flex;
    position: relative;
    height: 180px;
    width: 100%;
    background: linear-gradient(to bottom, #ffffff 0%,#d1e1ee 100%);
    transform: scale(1, 1);
}
#sbar .p-sidebar-header::before{
    content: "";
    display: block;
    position: absolute;
    border-radius: 100%;
    width: 100%;
    height: 300px;
    background: #204887;
    right: -25%;
    top: 156px;
}
#sbar .p-sidebar-header::after{
    content: "";
    display: block;
    position: absolute;
    border-radius: 100%;
    width: 100%;
    height: 300px;
    background: linear-gradient(to bottom, #ffffff 0%,#d1e1ee 100%);
    left: -27%;
    top: -100px;
    -webkit-clip-path: ellipse(100% 15% at -15% 100%);
    clip-path: ellipse(100% 15% at -15% 100%);
}
.wrapper-drop-sm .p-accordion .p-accordion-header .p-accordion-header-link{
    border: 0;
    background-color: transparent;
    padding-left: 0;
    padding-right: 0;
    color: #fff !important;
    flex-direction: row-reverse;
} 
.wrapper-drop-sm .p-accordion .p-accordion-header:not(.p-disabled).p-highlight .p-accordion-header-link{
    background: transparent;
    border-color: transparent;
    box-shadow: none;
}
.wrapper-drop-sm .p-accordion .p-accordion-header:not(.p-highlight):not(.p-disabled):hover .p-accordion-header-link{
    background: transparent;
    border-color: transparent;
    box-shadow: none;  
} 
.wrapper-drop-sm .p-accordion .p-accordion-content{
    background: transparent !important;
}
.wrapper-drop-sm .p-menu{
    background: transparent !important;
}
.wrapper-drop-sm .p-menu .p-menuitem>.p-menuitem-content{
    color: #fff;
    padding-top: .5rem;
    padding-bottom: .5rem;
} 
.wrapper-drop-sm .p-accordion .p-accordion-content{
    border-top: 1px solid #dee2e6;
    border-top-right-radius: 6px;
    border-top-left-radius: 6px;
}
.wrapper-nav-hover a:hover,
.wrapper-nav-hover a:focus{
    background: #2e75ab;
    display: block;
}
</style>