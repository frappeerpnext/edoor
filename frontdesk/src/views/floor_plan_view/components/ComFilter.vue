<template>
    <div class="grid">
        <div class="grid col-12 pr-0 justify-content-between ">
            <div class="col-12 py-0 pr-0 lg:col grid">
                <div class="col-12 lg:col-fixed w-full lg:w-auto ">
                    <InputText  class="w-full" v-model="filters.keyword" :placeholder="$t('Search')" v-debounce="onSearch" />
                </div>    
                <div class="col-6 lg:col-fixed lg:w-auto">
                    <Calendar :selectOtherMonths="true" class="w-full" :modelValue="filters.date" @date-select="onDateChange"
                        dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear" />
                </div>    
                <div class="col-6 lg:col-fixed lg:w-auto">
                    <ComSelect v-if="buildings.length > 1" :filters="[['property', '=', property_name]]"
                        :placeholder="$t('All Building')" v-model="filters.building" doctype="Building" optionLabel="name"
                        optionValue="name" class="w-full overflow-x-auto" :clear="true" @onSelected="onSelectBuilding"></ComSelect>

                         
                </div>
                <div class="col-6 lg:col-fixed lg:w-auto" v-if="floors"> 
                    <Button class="border-0" @click="toggle">{{filters.floor || $t('Select Floor')}}</Button>   
                    <Menu ref="show" :model="menus" :popup="true" style="min-width: 180px;">
                        <template #end> 
                            <Button class="bg-transparent border-0 w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround" :class="{ 'active_btn': filters.floor === b.name }" @click="onFloorClick(b)" v-for="(b, index) in floors"
                                :key="index">
                                {{ b.name }}
                            </Button>
                        </template>
                    </Menu>
                </div> 
            </div>
            <div style="height: 35px;" class="col-12 flex justify-content-end flex-wrap lg:col-fixed lg:w-auto  py-0">
                <Button  @click="onNextPrevDate(-1)" icon="pi pi-angle-double-left" v-tippy="$t('View Previous Day')" class="border-noround-right border-y-none border-left-none"></Button>
                <Button @click="onNextPrevDate(0)"  v-tippy ="$t('View Today')"  class="border-noround border-none">Today</Button>
                <Button @click="onNextPrevDate(1)"  v-tippy ="$t('View Next Day')" class="border-noround-left border-y-none border-right-none" icon="pi pi-angle-double-right"></Button> 
            </div>
        </div>    
    </div>

   
</template>
<script setup>
import { ref, onMounted, inject, getDocList, nextTick } from "@/plugin"
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
const buildings = ref([])
const floors = ref([])
const moment = inject('$moment')
const emit = defineEmits(["onFilter","onSearch"])

const property_name = window.property_name

const show = ref()
const toggle = (event) => {
    show.value.toggle(event); 
}; 

const filters = ref({ date: moment.utc(moment(window.current_working_date).format("YYYY-MM-DD")).toDate() })


function debounce(func, wait) {
    let timeout;

    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

function onDateChange(event) {
    filters.value.date = (moment.utc(moment(event).format("YYYY-MM-DD")).toDate())
    onFilter()

}
const onSearch = async () => {
    await nextTick()
    emit("onSearch", filters.value.keyword)
}
const onFilter = async () => {
    await nextTick()
    emit("onFilter", filters.value)
}

const onFilterDebounce = debounce(onFilter, 500);
 
function onFloorClick(floor) {
    filters.value.floor = floor.name
    onFilterDebounce()
}

function onSelectBuilding(event){
     onFilterDebounce()
}

function onNextPrevDate(n) {
    if (n == 0) {
        filters.value.date = moment.utc(moment(window.current_working_date).format("YYYY-MM-DD")).toDate()
    } else {
        filters.value.date = moment.utc(moment(filters.value.date).add(n, "days").format("YYYY-MM-DD")).toDate()


    }

    onFilterDebounce()

}

function getBulding() {
    return new Promise((resolve, reject) => {
        getDocList("Building", {
            fitlers: { property: property_name }
        }).then(result => {
            buildings.value = result
            // if (!filters.value.building) {
            //     filters.value.building = result[0].name
            // }
            resolve(result.message)
        }).catch(error=>{
            reject(error)
        })

    })
}


function getFloor() {
    return new Promise((resolve, reject) => {
        getDocList("Floor", {
            fields: ["name", "building"],
            fitlers: { property: property_name },

            orderBy: {
                field: 'sort_order',
                order: 'asc',
            },
        }).then(result => {
            floors.value = result

            if (!floors.value.floor) {
               
                filters.value.floor = result[0].name
            }
            resolve(result.message)

        }).catch(error => {
            reject(error)
        })
    })
}
onMounted(async () => {
    await getBulding()
    await getFloor()
    
    onFilter()



})

</script>