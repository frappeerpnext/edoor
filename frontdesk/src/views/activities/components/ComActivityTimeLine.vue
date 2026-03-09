<template>
    <Timeline :value="events" class="customized-timeline">
        <template #marker="slotProps">
            <template v-if="slotProps.item.date">
                <div class="flex bg-white border-none font-normal mt-3 border-round-xl py-2 px-6 white-space-nowrap"
                    style="font-weight: 400;">
                    <h1 v-if="slotProps.item.date == 'Today' || slotProps.item.date == 'Yesterday'"><strong>
                        {{ $t(slotProps.item.date) }}</strong></h1>
                    <h1 v-else><strong>
                            <ComTimeago :date="slotProps.item.date" />
                        </strong></h1>
                </div>
            </template>

            <span v-else
                class="flex w-2rem h-2rem bg-white align-items-center justify-content-center text-red border-circle z-1 shadow-1"
                :style="{ backgroundColor: slotProps.item.color }">
                <i :class="slotProps.item.custom_icon"></i>
            </span>

        </template>
        <template #content="slotProps">
            <Card class="mt-3" v-if="!slotProps.item.date">
                <template #title>
                    <div class="line-height-1">
                        <span class="text-lg md:text-xl">{{ $t(slotProps.item.subject) }}</span>

                        <div class="font-italic text-500 text-sm inline"
                            v-if="slotProps.item.custom_note_date && slotProps.item.custom_is_note"
                            style="font-size: 12px;font-weight: 500;">
                            | {{ $t('Note Date') }} : <span class="ms-1 font-italic text-500 text-sm">{{ slotProps.item.custom_note_date
                            }}</span>
                        </div>
                    </div>
                </template>

                <template #content>
                    <div class="grid w-full">
                        <div
                            class="col-fix w-20rem ms-3 flex white-space-nowrap overflow-hidden text-overflow-ellipsis flex align-content-center">
                            <div>
                                <ComAvatar :size="isMobile ? 'large'  : 'xlarge' " :label="slotProps.item.comment_by"
                                    :image="slotProps.item.custom_comment_by_photo" />
                            </div>
                            <div class="border-left-1 ms-1 ps-3 line-height-2">
                                <div class="flex gap-2 align-items-center">
                                    <div
                                        class="text-md md:text-lg font-bold white-space-nowrap overflow-hidden text-overflow-ellipsis">
                                        {{ slotProps.item.comment_by }}
                                    </div>
                                </div>

                                <div>
                                    {{ $t(slotProps.item.reference_doctype)  }}
                                </div>
                                <div class="cursor-pointer" style="color:#4338ca;" @click="onViewDetail(slotProps.item)">
                                    {{ slotProps.item.reference_name }}
                                </div>
                            </div>
                        </div>

                        <div class="col-12 md:col p-2 md:p-0" style="max-width:70vw;">
                            <div class="content-note-comment" v-html="slotProps.item.content">
                            </div>
                        </div>
                         <hr v-if="isMobile" class="w-full pb-3">
                        <div class="md:col-fix text-500 w-full md:w-10rem flex justify-content-end -mb-12 md:mb-0" style="font-size: 12px;font-weight: 400;">
                           
                            <ComTimeago :date="slotProps.item.creation"></ComTimeago>
                        </div>
                    </div>
                </template>
            </Card>
        </template>
    </Timeline>
</template>
<script setup>
import { ref, computed, inject, onMounted, onUnmounted } from "@/plugin"
import Timeline from 'primevue/timeline';
import ComAvatar from '@/components/form/ComAvatar.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const working_date = ref(window.current_working_date)
const moment = inject("$moment")
const isMobile = ref(window.isMobile) 
const props = defineProps({
    data: Object
})
const events = computed(() => {
    if (props.data) {

        const dates = [...new Set(props.data.map(r => r.custom_posting_date))]
        if (dates.length > 0) {
            let data = []
            dates.forEach(d => {
                if (d == working_date.value) {
                    data.push({ date: "Today" })
                }
                else if (d == moment(working_date.value).subtract(1, 'days').format('YYYY-MM-DD')) {
                    data.push({ date: "Yesterday" })

                }
                else {
                    data.push({ date: d })

                }
                data = [...data, ...props.data.filter(r => r.custom_posting_date == d)]



            })
            return data
        }
        return []
    }
    return []
})
function onViewDetail(d) {
    window.postMessage("view_" + d.reference_doctype.toLowerCase().replaceAll(" ", "_") + "_detail|" + d.reference_name, "*")
}

</script>