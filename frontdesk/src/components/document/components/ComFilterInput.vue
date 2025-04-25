
<template>
    <div class="card flex justify-content-center">
 
        <Button class="border-blue-200 content_btn_b h-full px-2 py-1 border-none" :severity="(hasFilter?'warning':'secondary')" type="button" @click="toggle" style="height: 30px !important;">
         <slot>
        
            {{ option?.label }} 
        
         </slot>
         <ComIcon v-if="hasDropDownIcon" class="ml-2" icon="arrowDown" style="width: 10px;"/>
        </Button>

        <OverlayPanel ref="op"  @show="onShow" class="filter_overlay_panel_custom">
            <Stack class="scroll-content">
                <h1 class="font-bold">{{ option.label }}</h1>
              
                <ComSelect v-if="!option.hideOperator" :options="operatorOptions"  optionLabel="label" optionValue="value" 
                  v-model="operator"
                  @onSelected="onOperatorChanged"
                  :clear="false"
                />
 
            
                <slot name="filter-template">
                <InputText 

                 ref="searchInput"
                v-model="keyword"
                :placeholder="'Search ' + option.label" class="w-full"
                 v-debounce="onSearch"
                 v-if="operator!='is'"
                 ></InputText>
                
              
                <Listbox v-model="selected" v-if="option.fieldtype == 'Link' && operator!='is'"
                 :options="listData"
                 :optionValue="optionValue"
                 @change="onSelectOptionChange"
                 :multiple="operator=='in' || operator=='not in'" 

                 class="w-full md:w-56 filter_content_custom">
                    <template #option="slotProps">
                        <Stack gap="2px">
                            <h1 class="font-bold">{{ slotProps.option.label || slotProps.option.value }}</h1>
                            <p v-if="slotProps.option.description">{{ slotProps.option.description }}</p>
                        </Stack>
                    </template>
                </Listbox>
            </slot>
            <ComSelect 
                  v-if="operator=='is'"
                 :options="[{label:'Set',value:'set'},{label:'Not Set',value:'not set'}]"  optionLabel="label" optionValue="value" 
                  v-model="selected"
                  @onSelected="onSearch"
                  :clear="false"
                  placeholder="Select Value"
                />
            </Stack>

            <slot name="bottom"></slot>
            
        </OverlayPanel>
    </div>
</template>

<script setup>
import { ref ,nextTick } from "vue";
const emit = defineEmits();
const props = defineProps({
    option:Object,
    operatorOptions:Object,
    hasFilter:Boolean,
    optionValue:{
        type:String,
        default:"value"
    },
    hasDropDownIcon: {
        type: Boolean,
        default: true
    }
    
})
const operator = defineModel('operator')
const keyword = defineModel('keyword')
const listData = defineModel('listData')
const selected = defineModel('selected')

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
    selected.value = null

    if(keyword.value){
        emit("onSearch")
    }
}

function onSearch(){
    emit("onSearch")
    
}

function onSelectOptionChange(){
   emit("onFilter")
}

const onShow = () => {
    nextTick(() => {
        searchInput.value?.$el?.focus();
        if(!loaded.value){
            emit("onLoadOptionData")
        }
        loaded.value = true

    });
};
</script>
