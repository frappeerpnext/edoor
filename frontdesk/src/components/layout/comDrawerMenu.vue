<template>
    <Button icon="pi pi-bars" style="background: transparent" class="border-none" @click="visible = true" />

    <Sidebar v-model:visible="visible">
        <template #header>
            <div>
                <div class="profile bg-primary w-4rem h-4rem border-circle overflow-hidden">
                    <img class="image-profile w-full h-full" style="object-fit: cover;" :src="user.photo"/>
                </div>
                <h1 class="text-2xl font-semibold pt-3 text-white">{{user.full_name}}</h1>
                <p class="text-white">rathanachamroeun155@gmail.com</p>
            </div>
        </template>
        <hr/>
        <div class="pt-3">
            <template v-for="(item, index) in items" :key="index">
                <div v-if="!item.items">
                    <a v-ripple @click="onNavigate(item)">
                        <span class="ml-2">{{ item.label }}</span>
                    </a>
                </div>
                <div v-else>
                    <Accordion>
                        <AccordionTab   >
                            <template #header>
                                <span class="flex align-items-center gap-2 w-full">
                                <Avatar image="https://primefaces.org/cdn/primevue/images/avatar/amyelsner.png" shape="circle" />
                                <span class="font-bold white-space-nowrap">{{ item.label }}</span>
                                </span>
                            </template>

                            <Menu :model="item.items" class="w-full md:w-15rem">
                                <template #item="{ item, props }">
                                    <a v-ripple @click="onNavigate(item)">
                                        <span class="ml-2">{{ item.label }}</span>
                                    </a>


                                </template>
                            </Menu>
                        </AccordionTab>

                    </Accordion>
                </div>
            </template> 
        </div>
    </Sidebar>
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
.p-sidebar-header{
    overflow: hidden;
    display: block;
    position: relative;
    height: 40px;
    width: 100%;
    background: rgb(57, 27, 112);
    transform: scale(1, 1);
}
.p-sidebar-header::before{
    content: "";
    display: block;
    position: absolute;
    border-radius: 100%;
    width: 100%;
    height: 300px;
    background-color: white;
    right: -25%;
    top: 20px;
}
.p-sidebar-header::after{
    content: "";
    display: block;
    position: absolute;
    border-radius: 100%;
    width: 100%;
    height: 300px;
    background-color: rgb(57, 27, 112);
    left: -25%;
    top: -240px;
    clip-path: ellipse(100% 15% at -15% 100%);
}
</style>