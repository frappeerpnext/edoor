<template>

  <ComBoxStayInformation title="Adults" 
                        valueClass="col-2 color-purple-edoor" class_action="link_line_action"   :value="7"
                        >
                    </ComBoxStayInformation>
                   
<OverlayPanel ref="op"> 
    <h1>Change Pax</h1>
    <InputNumber v-model="adult" inputId="stacked-buttons" showButtons :min="1"
                                :max="100" class="child-adults-txt" />

    <InputNumber v-model="child" inputId="stacked-buttons" showButtons :min="0"
                                :max="100" class="child-adults-txt" />
                                <Divider />
                                <Button @click="onSave">Save</Button>
</OverlayPanel>


</template>
<script setup>
import {ref,useToast} from "@/plugin"
import OverlayPanel from 'primevue/overlaypanel';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const op = ref();
const toast =useToast()

const toggle = (event) => {
   
    op.value.show()
}
const adult =ref(1)
const child =ref(0)
const onSave = ()=>{
    toast.add({ severity: 'success', summary: 'Change Pax', detail: "Change pax successfully", life: 3000 })
    op.value.hide();
}

function xx(){
    alert(111)
}

</script>
