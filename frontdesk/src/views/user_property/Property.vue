<template>
    <ComDialogContent :isDialog="false">
        <div class="pro__wrapper_dialog dialog_change_pro px-5" v-if="isModal">
            <div class="grid grid-rows-4 grid-flow-col gap-4 pt-2">
                <template v-for="(p, index) in current_user.property.filter(r => r.name != current_property?.name)"
                    :key="index">
                    <Button class="btn-choose__pro" @click="onChangeProperty(p)">
                        <div>
                            <div class="mb-3 font-medium">{{ p.name }}</div>
                            <div class="flex w-full justify-center">
                                <div class="profile-photo flex place-items-center justify-center">
                                    <Avatar size="xlarge" :image="p.photo" :icon="p.photo ? '' : 'pi pi-building'"
                                        class=" w-6rem h-6rem bg-gray-300 border-circle border-1" shape="circle" />
                                </div>
                            </div>
                            <div class="mt-3 text-base">{{ p.phone_number_1 }}</div>
                        </div>
                    </Button>
                </template>
            </div>
        </div>
        <div class="mx-auto w-full text-center flex place-items-center justify-center landing-page-custom" v-else>
            <div>
                <div class="h__between-content">
                    <h1 class="text-5xl">Select property</h1>
                    <p>Below is the list of property, please select!</p>
                </div>
                <div class="grid grid-rows-4 grid-flow-col gap-4">
                    <template v-for="(p, index) in current_user.property" :key="index">
                        <Button class="btn-choose__pro" @click="onChangeProperty(p)">
                            <div>
                                <div class="mb-3 font-medium">{{ p.name }}</div>
                                <div class="flex w-full justify-center">
                                    <div class="profile-photo flex place-items-center justify-center">
                                        <Avatar size="xlarge" :image="p.photo" :icon="p.photo ? '' : 'pi pi-building'"
                                            class="w-6rem h-6rem bg-gray-300 border-circle border-1" shape="circle" />
                                    </div>
                                </div>
                                <div class="mt-3 text-base">{{ p.phone_number_1 }}</div>
                            </div>
                        </Button>
                    </template>
                </div>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted } from '@/plugin'
import ComDialogContent from '../../components/form/ComDialogContent.vue';
const dialogRef = inject("dialogRef");
const isModal = ref(false)
const current_user = JSON.parse(localStorage.getItem("edoor_user"))
const current_property = JSON.parse(localStorage.getItem("edoor_property"))

function onSelectProperty(property) {
    localStorage.setItem("edoor_property", JSON.stringify(property));
    dialogRef.value.close(property);

}
function onChangeProperty(property) {
    localStorage.setItem("edoor_property", JSON.stringify(property));
    location.reload();

}

onMounted(() => {
    if (!dialogRef) {
        isModal.value = false
    } else {
        isModal.value = true;
    }
});

</script>
<style ></style>