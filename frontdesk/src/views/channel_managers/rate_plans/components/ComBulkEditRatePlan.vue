<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Save" :hideIcon="false">

        <div class="grid">
            <div class="col-6 font-bold">Start Date</div>
            <div class="col-6 font-bold">End Date</div>

        </div>
        <div class="grid" v-for="(d, index) in data.date_range" :key="idx">

            <div class="col-6">

                <Calendar :selectOtherMonths="true" v-model="d.start_date" dateFormat="dd-mm-yy" showButtonBar showIcon
                    panelClass="no-btn-clear" class="w-full" />
            </div>
            <div class="col-6">
                <div class="flex">
                    <Calendar :selectOtherMonths="true" v-model="d.end_date" dateFormat="dd-mm-yy" showButtonBar showIcon
                        panelClass="no-btn-clear" class="w-full" />
                    <Button icon="pi pi-times" v-if="data.date_range.length > 1" severity="danger" text aria-label="Button"
                        @click="onDeleteDateRange(index)" />
            
                </div>
            </div>
        </div>
        <div class="flex justify-content-end mt-4">
            <Button label="Add Date Range" class="border-0" @click="onAddDateRange" v-if="data.date_range.length < 12" />
        </div>
        <Message severity="warn">{{$t("If the value is left empty, the price will remain unchanged. If the price is set to 0, the price will be updated to 0.")}}</Message>


        <div class="flex gap-2 mb-5">
            <Chip label="All Room Types" @click="onEnableUpdateAllRoomType()"
                :icon="(updateRoomTypes.size == roomTypes.length) ? 'pi pi-check' : ''" :class="(updateRoomTypes.size == roomTypes.length) ? 'p-chip-selected' : ''" class="cursor-pointer select-none"></Chip>
            <Chip :label="rt.room_type_name" :icon="(updateRoomTypes.has(rt.edoor_room_type)) ? 'pi pi-check' : ''"
                @click="onToggleRoomTypeToUpdate(rt.edoor_room_type)" v-for="rt in roomTypes"
                :key="'rt_selection' + rt.edoor_room_type" :class="(updateRoomTypes.has(rt.edoor_room_type)) ? 'p-chip-selected' : ''" class="cursor-pointer select-none"/>

        </div>
        <table class="p-datatable-table">
            <thead>
                <tr>
                    <th class="text-left">
                        Occupancy <br />
                        Room Type
                    </th>
                    <th v-for="rt in data.room_types" class="text-left">
                        {{ rt.room_type_name }} - ({{ rt.cm_room_type }})
                    </th>
                </tr>

            </thead>
            <tbody>
                <tr v-for="occ in occupancyCodes">
                    <td>{{ occ.title }}</td>
                    <td v-for="rt in data.room_types" class="input-rate-price">
                        <template v-if="rt.occupancy_codes.find(x => x.occupancy_code == occ.occupancy_code)">

                            <ComInputCurrency :disabled="!updateRoomTypes.has(rt.edoor_room_type)" classCss="w-full"
                                v-model="rt.occupancy_codes.find(x => x.occupancy_code == occ.occupancy_code).rate" />
                        </template>
                    </td>
                </tr> 
            </tbody>
        </table>


    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted } from 'vue';
import { useRatePlan } from '../hooks/useRatePlan';
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const dialogRef = inject("dialogRef");
const updateRoomTypes = ref(new Set())
const oldRoomRates = ref({})
const {
    roomTypes,
    selectedDates,
    occupancyCodes,
    selectedRoomTypes
} = useRatePlan()
const moment = inject('$moment')
const rate_type = ref("")
const data = ref({
    rate_type: dialogRef.value.data.rate_type,

    room_types: [],
    date_range: [
        {
            start_date: moment().toDate(),
            end_date: moment().add(1, "day").toDate(),
        }
    ]
})

function onToggleRoomTypeToUpdate(room_type) {
    if (updateRoomTypes.value.has(room_type)) {
        updateRoomTypes.value.delete(room_type)
    } else {
        updateRoomTypes.value.add(room_type)
    }
}
function onEnableUpdateAllRoomType(room_type) {
    if (updateRoomTypes.value.size == roomTypes.value.length) {
        // remove 
        updateRoomTypes.value = new Set()
    } else {
        roomTypes.value.forEach(x => {
            updateRoomTypes.value.add(x.edoor_room_type)
        })
    }

}

function onAddDateRange() {
    const last_end_date = data.value.date_range[data.value.date_range.length - 1].end_date;
    data.value.date_range.push({
        start_date: moment(last_end_date).add(1, "day").toDate(),
        end_date: moment(last_end_date).add(2, "day").toDate()
    })
}

function onDeleteDateRange(idx) {
    data.value.date_range.splice(idx, 1)
}

function validate() {
    if (updateRoomTypes.value.size == 0) {
        app.showWarning($t("Please select room type to update rate"))
        return false
    }
    if (!data.value.date_range) {
        app.showWarning($t("Please enter start date and end date"))
        return false
    }

    const hasInvalidDate = data.value.date_range.some((dt, index) => {
        if (!dt.start_date) {
            app.showWarning(
                $t(`Please enter start date at row range ${index + 1}`)
            )
            return true
        }

        if (!dt.end_date) {
            app.showWarning(
                $t(`Please enter end date at row range ${index + 1}`)
            )
            return true
        }
    })
    if (hasInvalidDate) return false;


    return true
}

async function onOk() {

   

    if (!validate()) return;

    const saveData = JSON.parse(JSON.stringify(data.value))
    // fitler room type 
    saveData.room_types = saveData.room_types.filter(x => Array.from(updateRoomTypes.value).includes(x.edoor_room_type))

    saveData.date_range.forEach(x => {
        x.start_date = moment(x.start_date).local().format("YYYY-MM-DD");
        x.end_date = moment(x.end_date).local().format("YYYY-MM-DD");
    })
    saveData.room_types.forEach(rt => {
        rt.occupancy_codes = rt.occupancy_codes.filter(x => x.rate != null)
    })

    const l = await window.showLoading("Update room rate...")

    const res = await app.postApi("rate_plan.bulk_update_room_rate", {
        data: saveData
    })
    l.close();



    if (res.data) {
        resetRate();
        dialogRef.value.close(true)
    }

}

function resetRate() {
    roomTypes.value.forEach(rt => {
        rt.occupancy_codes.forEach(x => {
            delete x["rate"]
        })

    });
}

async function checkRoomRate() {

    const res = await app.postApi("rate_plan.check_room_rate_on_update", {
        data: {
            property: property.name,
            rate_type: rate_type.value,
            dates: data.value.date_range.map(x => {
                return {
                    start_date: moment(x.start_date).local().format("YYYY-MM-DD"),
                    end_date: moment(x.end_date).local().format("YYYY-MM-DD")
                }
            }),
            room_types: roomTypes.value.map(x => x.edoor_room_type)
        }
    },
        "", false)
    if (res.data) {
        oldRoomRates.value = res.data
    }

}
onMounted(async () => {
    const l = await window.showLoading();

    rate_type.value = dialogRef.value.data.rate_type
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    data.value.property = property.name


    if (selectedDates.value.size > 0) {
        const dates = app.utils.groupDatesToPeriods(selectedDates.value);
        data.value.date_range = dates.map(x => {
            return {
                start_date: moment(x.start_date).toDate(),
                end_date: moment(x.end_date).toDate()
            }
        })
    }

    // setup room rate data  by occpancy codes
    updateRoomTypes.value.add(roomTypes.value.find(x => x.selected).edoor_room_type)
    // check rate from server 
    await checkRoomRate();

    roomTypes.value.forEach(rt => {
        const occpancy_data = rt.occupancy_codes
        occpancy_data.forEach(x => {

            x.rate = oldRoomRates.value[x.room_type_id + "_" + x.occupancy_code]
        })

        data.value.room_types.push({
            room_type_name: rt.room_type_name,
            cm_room_type: rt.cm_room_type,
            edoor_room_type: rt.edoor_room_type,
            occupancy_codes: occpancy_data
        })

    });
    l.close();



})
</script>
<style scoped>
.p-chip-selected {
    background-color: var(--primary-color) !important;
    color: var(--primary-color-text) !important;
}
</style>