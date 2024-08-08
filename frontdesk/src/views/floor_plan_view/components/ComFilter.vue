<template>
    {{ filters }}
    <InputText  v-model="filters.keyword" :placeholder="$t('Search')" v-debounce="onSearch" />

    <div>
        <Calendar :selectOtherMonths="true" class="w-full" :modelValue="filters.date" @date-select="onDateChange"
            dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear" />
    </div>
    <div>

        <ComSelect v-if="buildings.length > 1" :filters="[['property', '=', property_name]]"
            :placeholder="$t('Building')" v-model="filters.building" doctype="Building" optionLabel="name"
            optionValue="name" class="w-full overflow-x-auto"></ComSelect>

    </div>


    <div v-if="floors">
        <Button @click="onFloorClick(b)" v-for="(b, index) in floors.filter(r => r.building == filters.building)"
            :key="index">
            {{ b.name }}
        </Button>
    </div>
    <Button @click="onNextPrevDate(1)">Next Date</Button>
    <Button @click="onNextPrevDate(-1)">Prev Date</Button>
    <Button @click="onNextPrevDate(0)">Today</Button>
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
            if (!filters.value.building) {
                filters.value.building = result[0].name
            }
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