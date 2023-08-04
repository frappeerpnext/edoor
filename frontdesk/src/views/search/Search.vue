<template >
    <ComDialogContent :is-dialog="false" :hideFooter="true">
        <div class="d-flex w-full">
            <span class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText  class="w-full unrounded__box_cus bg-transparent" v-model="value1" placeholder="Search" @input="onSearch" />
            </span>
        </div>        
    </ComDialogContent>
</template>
<script setup>
import ComDialogContent from '../../components/form/ComDialogContent.vue';
function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}
const onSearch = debouncer(() => {
    loadData();
}, 500);

function loadData() {
    alert("world")
}

</script>
<style ></style>