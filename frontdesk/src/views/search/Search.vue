<template >
    <ComDialogContent :is-dialog="false">
        <div class="d-flex w-full">
            <span class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText class="w-full unrounded__box_cus bg-transparent" v-model="value1" placeholder="Search" />
            </span>
        </div>
    </ComDialogContent>
</template>
<script setup>
import ComDialogContent from '../../components/form/ComDialogContent.vue';


</script>
<style ></style>