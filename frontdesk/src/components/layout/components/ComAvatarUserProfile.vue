<template>
    <div @click="onClick" class="guest-user__pro px-2 flex items-center h-full justify-center cursor-pointer"
         aria-haspopup="true" aria-controls="overlay_menu_user">

        <ComAvatar :image="user.photo">
            <div :title="user.full_name"
                :style="(user.full_name.length > 12) ? { fontSize: 12.90 - (user.full_name.length - 14) * 0.10 + 'px' } : ''"
                class="hidden md:block font-lg font-bold text-white white-space-nowrap overflow-hidden text-overflow-ellipsis w-8rem ms-3">{{
                    user.full_name
                }}</div>
            <div :title="user.role" class="hidden md:block text-ms text-white white-space-nowrap overflow-hidden text-overflow-ellipsis ms-3">{{
                user.role }}</div>
        </ComAvatar>
    </div>
    <Menu ref="show" id="overlay_menu_user" :popup="true" style="min-width: 180px;">
        <template #end>
            <button @click="onRefresh"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="font-bold pi pi-refresh" />
                <span class="pl-2 pr-3">{{$t("Refresh")}}</span>
            </button>
            <button @click="onOpenBackend"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="font-bold pi pi-server" />
                <span class="pl-2 pr-3">{{$t("Open Backend")}}</span>
            </button>
            <button @click="onShortCutMenu"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="font-bold pi pi-key" />
                <span class="pl-2 pr-3">{{$t("Shortcut Menu")}}</span>
            </button>
            <button @click="showChangeLanguage"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="pi pi-language" />
                <span class="pl-2 pr-3">{{ $t("Change Language") }}</span>
            </button>



            <button @click="onRoute"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="font-bold pi pi-book" />
                <span class="pl-2 pr-3"> {{$t("Help Document")}}</span>
            </button>
            <button @click="onLogout"
                class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                <i class="font-bold pi pi-sign-out !text-red-500" />
                <span class="pl-2 pr-3 !text-red-500">{{$t("Log Out")}}</span>
            </button>
        </template>
    </Menu>
</template>
<script setup>
import { ref, inject, useDialog } from '@/plugin'
import ComIFrameModal from "@/components/ComIFrameModal.vue"
import {i18n} from '@/i18n';
import ComChangeLanguage from '@/components/layout/components/ComChangeLanguage.vue';
const gv = inject("$gv")
const auth = inject("$auth")
const show = ref()
const dialog = useDialog()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol=="http:"?"http://" + window.location.hostname + ":" + window.setting.backend_port:"https://" + window.location.hostname;

 
const { t: $t } = i18n.global;

const props = defineProps({
    user: Object
})

function onLogout() {
    auth.logout().then(() => {

        location.replace(serverUrl)

    }).catch((error) => toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 }));
}
function onRoute() {
    window.open(setting.help_url)
}
const onClick = (event) => {
    show.value.toggle(event);
};
function onRefresh() {

    window.location.reload();
}
function onOpenBackend () { 
    window.open(serverUrl + '/' + 'app')
}
function showChangeLanguage() {

const dialogRef = dialog.open(ComChangeLanguage, {
    props: {
        header: 'Change Language',
        style: {
            width: '30vw',
        },
        maximizable: true,
        modal: true,
        closeOnEscape: false,
        position: "top",
        breakpoints:{
            '960px': '80vw',
            '640px': '100vw'
        },
    }
});
}
function onShortCutMenu() {
    dialog.open(ComIFrameModal, {
        data: {
            doctype: "Business Branch",
            name: window.property_name,
            report_name: gv.getCustomPrintFormat("eDoor Shortcut Menu Help"),
            view: "ui"
        },
        props: {
            header: "Shortcut Menu",
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    });

}


</script>