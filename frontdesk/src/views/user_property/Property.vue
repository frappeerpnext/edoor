<template>
    {{ current_user.property }}
    <div class="pro__wrapper_dialog" v-if="isModal">
        <template v-for="(p, index) in current_user.property.filter(r => r.name != current_property?.name)" :key="index">
            <Button class="btn-choose__pro mr-2" @click="onSelectProperty(p)">
                {{ p.name }}
            </Button>
        </template>
    </div>
    <div v-else>
        <h1>Hi Rathana pls help format this in Property.vue</h1>
        <template v-for="(p, index) in current_user.property.filter(r => r.name != current_property?.name)" :key="index">
            <Button class="btn-choose__pro mr-2" @click="onChangeProperty(p)">
                {{ p.name }}
            </Button>
        </template>
    </div> 
</template>
<script setup>
import { ref, inject ,onMounted} from '@/plugin'
const dialogRef = inject("dialogRef");
const isModal = ref(false)
const current_user = JSON.parse(localStorage.getItem("edoor_user"))
const current_property = JSON.parse( localStorage.getItem("edoor_property"))

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