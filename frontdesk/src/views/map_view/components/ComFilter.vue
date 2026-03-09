<template>
    <div class="page-form rounded-lg">
        <div class="form-group frappe-control input-max-width md:w-full">
            <div class="flex gap-2">
              <div class="">
                <ComSelect :clear="false" :options="timespanOption" v-model="filters.timespan"
                    @onSelected="onRefreshData" :placeholder="$t('Date')" class="w-full overflow-x-auto" />
              </div>
                 <Calendar class="w-full" :selectOtherMonths="true" hideOnRangeSelection
                    v-if="filters.timespan == 'Date Range'" dateFormat="dd-MM-yy" v-model="filters.date_range"
                    selectionMode="range" :manualInput="false" @date-select="onSelectDateRange"
                    placeholder="Select Date Range" showIcon />
   
              <div class="w-auto">
                  <ComSelect :filters="[['property', '=', property_name]]" :placeholder="$t('All Room Types')"
                    v-model="filters.room_type" doctype="Room Type" optionLabel="room_type" optionValue="name"
                    class="w-full overflow-x-auto" @onSelected="onRefreshData"></ComSelect>
              </div> 
              <div class="w-auto">
                  <ComAutoComplete isFull :filters="[['property', '=', property_name]]"
                    :placeholder="$t('All Business Source')" v-model="filters.business_source" doctype="Business Source"
                    optionLabel="business_source" optionValue="name" class="w-full overflow-x-auto"
                    @onSelected="onRefreshData" />
              </div>
              <div class="w-auto">
                <ComSelect :clear="false" v-if="columns" :options="columns.filter(r => r.fieldtype)"
                    v-model="filters.display_field" optionLabel="label" optionValue="fieldname"
                    class="w-full overflow-x-auto" />  
              </div>  
                <!-- <div :class="bodyClass"> -->
                
                <!-- </div> -->
                
            </div>
        </div>
    </div>

</template>
<script setup>
import { ref,inject } from "@/plugin"
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
const moment = inject("$moment");
const property_name = window.property_name

const props = defineProps({
    filters:Object,
    columns:Object
})

const emit = defineEmits(['update:modelValue','onFilter'])
const timespanOption = ref([
  "Today",
  "Yesterday",
  "This Month",
  "Next Month",
  "Last Month",
  "This Year",
  "Last Year",
  "Date Range",
]);

const onSelectDateRange = (data) => {
  if (props.filters.date_range){
    if (!props.filters.date_range[0]){
      delete props.filters["start_date"]
    }else {
      props.filters.start_date = moment(props.filters.date_range[0]).format("YYYY-MM-DD")
    }
    if (!props.filters.date_range[1]){
      delete props.filters["end_date"]
    }else {
      props.filters.end_date = moment(props.filters.date_range[1]).format("YYYY-MM-DD")
    }
  }
  
  emit("onFilter",props.filters)
};

function onRefreshData(){
    emit("onFilter",props.filters)
}

</script>