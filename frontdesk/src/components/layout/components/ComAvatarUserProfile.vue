<template>
    <div @click="onClick" class="guest-user__pro px-2 flex items-center h-full justify-center cursor-pointer"
        style="width:180px" aria-haspopup="true" aria-controls="overlay_menu_user">
        <ComAvatar :image="user.photo">
            <div :title="user.name"
                class="font-lg font-bold text-white white-space-nowrap overflow-hidden text-overflow-ellipsis">{{ user.name
                }}</div>
            <div :title="user.role" class="text-ms text-white white-space-nowrap overflow-hidden text-overflow-ellipsis">{{
                user.role }}</div>
        </ComAvatar>
    </div>
    <Menu ref="show" id="overlay_menu_user" :popup="true" style="min-width: 180px;">
        <template #end>
            <button @click="onRefresh"
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-refresh" />
                                        <span class="ml-2">Refresh</span>
                                    </button>
            <button @click="onLogout"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="pi pi-sign-out !text-red-500" />
                <span class="ml-2  !text-red-500">Log Out</span>
            </button>
        </template>
    </Menu>
</template>
<script setup>
import { ref,inject } from '@/plugin'
const auth = inject("$auth")
const show = ref()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const props = defineProps({
    user: Object
})
function onLogout() {
    auth.logout().then(() => {
        
        location.replace(serverUrl)
        
    }).catch((error) => toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 }));
}

const onClick = (event) => {
    show.value.toggle(event);
};
function onRefresh() {

window.location.reload();
}


</script>