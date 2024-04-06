<template>
    <!-- {{ reports }} -->
    <div class="p-2">
        <div class="mb-3">
            <InputText class="w-full" v-model="keyword" :placeholder="$t('Search Report')" />
        </div>
        <div v-if="!loading">
            <Accordion :activeIndex="0" @tab-click="onTabClick">
                <AccordionTab :header="$t(p.report_title)"
                    v-for="(p, index) in reports?.filter(r => r.is_group == 1 && r.parent_system_report && r.has_child)"
                    :key="index">
                    <Listbox v-model="selectedReport" :options="reports?.filter(r => r.parent_system_report == p.name)"
                        optionLabel="report_title" optionValue="name" @change="onSelect" class="w-full" />
                </AccordionTab>
            </Accordion>
        </div>
    </div>
</template>
<script setup>
import { ref, getDocList, onMounted, computed } from "@/plugin"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const emit = defineEmits(["onSelectReport","onTabClick"])
const selectedReport = ref()
const data = ref()
const keyword = ref("")
const loading = ref(false)
const reports = computed(() => {
    if (keyword.value) {
        data.value?.filter(f => f.is_group == 1).forEach(r => {
            r.has_child = data.value?.filter(x => x.is_group == 0 && x.parent_system_report == r.name && x.report_title?.toLowerCase().includes(keyword.value.toLowerCase())).length > 0
        });
        return data.value
    } else {
        data.value?.filter(f => f.is_group == 1).forEach(r => {
            r.has_child = data.value?.filter(x => x.is_group == 0 && x.parent_system_report == r.name).length > 0
        });
        return data.value
    }
})

function onSelect(p) { 
    emit("onSelectReport", data.value.find(r => r.name == p.value))
}

function onTabClick () {
    emit("onTabClick")
}

onMounted(() => {
    loading.value = true;
    getDocList("System Report", {
        fields: ["name", "is_group", "report_title", "report_name", "filter_option", "parent_system_report"],
        orderBy: {
            field: "sort_order",
            order: "asc"
        },
        limit: 1000,
    }).then((result) => {
        const translatedResults = result.map(item => ({
        ...item,
        report_title: $t(item.report_title),
      }));
        data.value = translatedResults
  
        loading.value = false;
    }).catch((err) => {
        loading.value = false;
    })

})

</script>