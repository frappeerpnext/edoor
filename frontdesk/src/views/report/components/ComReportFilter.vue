<template>
    <div class="flex justify-between">
        <div class="grid">
            <div class="col-6" v-if="hasFilter('start_date')">
                <label>Start Date</label><br/>
                <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date" dateFormat="dd-mm-yy"
                    showIcon />
            </div>
            <div class="col-6" v-if="hasFilter('end_date')">
                <label>end date</label><br>
                <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date" dateFormat="dd-mm-yy"
                    showIcon />
            </div>
            <div class="col-6">
                <label>Business Source</label><br>
                <ComAutoComplete v-model="filter.business_source" placeholder="Business Source" doctype="Business Source"
                class="auto__Com_Cus w-full" :filters="{ property: property.name }" v-if="hasFilter('business_source')" />
            </div>
            <div class="col-6">
                <label>Letter Head</label><br>
                <ComSelect v-model="filter.letterhead" doctype="Letter Head" />
            </div>
            <div class="col-6">
                <label>Language</label><br>
                <ComSelect v-model="filter._lang" doctype="Language" optionLabel="language_name" optionValue="name"
                :filters="[['enabled', '=', 1]]" />
            </div>
        </div>
        <div class="flex align-items-end">
            <Button class="border-none white-space-nowrap" @click="onSearch">Preview Report</Button>
        </div>
    </div>
</template>
<script setup>
import { ref, inject } from "@/plugin"
const emit = defineEmits(['onFilter'])

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const user = JSON.parse(localStorage.getItem("edoor_user"))
const property = setting.property
const moment = inject("$moment")
const props = defineProps({
    selectedReport: Object,
    filter: Object

})
const filter = ref({
    letterhead: setting.property.default_letter_head,
    _lang: user.language || "en",
    start_date: moment().toDate(),
    end_date: moment().toDate()
})

const hasFilter = ref((f) => {
    if (props.selectedReport) {
        return props.selectedReport.filter_option?.includes(f)
    }
    return false

});

function onSearch() {
    let f = {}
    const filter_option = props.selectedReport.filter_option + ",_lang,letterhead"
    if (filter_option) {
        filter_option.split(",").forEach(r => {

            f[r.trim()] = filter.value[r.trim()]

        })
    }

    if (f.start_date) {
        f.start_date = moment(f.start_date).format("YYYY-MM-DD")
    }

    if (f.end_date) {
        f.end_date = moment(f.end_date).format("YYYY-MM-DD")
    }

    emit("onFilter", f)
}
</script>