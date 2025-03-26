
<template>
    <div class="card flex justify-content-center">
        <Button type="button"  @click="toggle">
         <slot>
         
            {{ selected || option?.label }} 
        
         </slot>
        </Button>

        <OverlayPanel ref="op"  @show="onShow">
            <Stack>
                <ComSelect :options="operatorOptions"  optionLabel="label" optionValue="value" 
                  v-model="operator"
                  @onSelected="onOperatorChanged"
                  :clear="false"
                />
 
            
              
                <InputText 
                 ref="searchInput"
                v-model="keyword"
                :placeholder="'Search ' + option.label" class="w-25rem"
                 v-debounce="onSearch"
                 v-if="operator!='is'"
                 ></InputText>
                 <ComSelect 
                  v-if="operator=='is'"
                 :options="[{label:'Set',value:'set'},{label:'Not Set',value:'not set'}]"  optionLabel="label" optionValue="value" 
                  v-model="keyword"
                  @onSelected="onSearch"
                  :clear="false"
                  placeholder="Select Value"
                />

            
              
            </Stack>
            
        </OverlayPanel>
    </div>
</template>

<script setup>
import { ref ,nextTick } from "vue";
const emit = defineEmits();
const props = defineProps({
    option:Object,
    operatorOptions:Object
})
const operator = defineModel('operator')
const keyword = defineModel('keyword')

const searchInput = ref(null);
const loaded = ref(false)
 
 

const op = ref();
 

const toggle = (event) => {
    op.value.toggle(event);
}

function onOperatorChanged(){
    if(operator.value=='is'){
        keyword.value = ''
    }
    if(keyword.value){
        emit("onSearch")
    }
}

function onSearch(){
 
    emit("onSearch")
    
}

const onShow = () => {
    
    nextTick(() => {
        searchInput.value?.$el?.focus();
        loaded.value = true

    });
};
</script>
