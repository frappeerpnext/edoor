<template>
    <div class="overflow-auto h-full mb-3">
            <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="notes.length > 0">
                <div class="grid-cs-note">
      <div v-for="(i, index) in notes" :key="index" :style="{ order: index }"
                         class="item-cs-note border-1 rounded-lg bg-white py-3 px-5 shadow-md note-content-box relative">
                        <div class="flex flex-col">
                            <div class="line-height-1 w-full flex justify-between ">
                                <div class="my-auto">
                                    <div v-if="i.reference_doctype">
						<span class="text-lg" >
							{{ i.reference_doctype }}
						</span>
						-
						<div @click="onViewDetail(i)" class="text-lg inline link_line_action  border-none p-0 w-auto" >
							 {{ i.reference_name }}
						</div>
						</div>
                        <div v-else>
							<span class="text-lg" >
								General Note
						</span>
                        </div>
                        
                                </div>
                                <div class="flex absolute right-3 gap-2">
                                    <Button :class="i.custom_is_pin ? '' : 'hidden'" class="w-2rem h-2rem px-1 pb-1 pt-0 btn-in-note "
                                        text rounded @click="onPin(i)">
                                        <ComIcon v-tippy ="'Unpin Note'" v-if="i.is_pin" icon="pushPined"
                                            style="height:20px;"></ComIcon>
                                        <ComIcon v-tippy ="'Pin Note'" v-else icon="pushPin" style="height:20px;">
                                        </ComIcon>
                                    </Button>
                                </div>
                            </div>
                            <div class="text-500 text-sm"> 
                                Note Date: {{ gv.dateFormat(i.custom_note_date) }} </div>
                        </div>
                        {{ i.room}}
                        {{ i.guest_name }}
                        <div v-if="i.content"
                            class="mt-3 mb-6 whitespace-pre-wrap break-words overflow-auto pb-5 line-height-2">
                            {{ i.content }}
                        </div>

                        <div class="flex flex-col font-italic  line-height-2 absolute bottom-2 modifiad-note-cs"
                            style="font-size: 10px;">
                            <div>
                                Noted by <span class=" text-500 "> {{ i.comment_by }} - <ComTimeago :date="i.creation"></ComTimeago></span>
                            </div>
                            <div v-if="i.modified">
                                Last Modified by : <span class=" text-500 ">{{ i.modified_by.split("@")[0] }} -
                                    <ComTimeago :date="i.modified" /></span>
                            </div>
                            <div class="absolute right-2">
                                <div class="flex">
                                    <Button class="w-2rem h-2rem flex justify-center items-center " text rounded outlined
                                        label="Edit" @click="onEdit(i.name)">
                                        <i class="pi pi-pencil text-blue-500"></i>
                                    </Button>
                                    <Button class="w-2rem h-2rem flex justify-center items-center " @click="onDelete(i.name)"
                                        text rounded outlined aria-label="Delete">
                                        <i class="pi pi-trash text-red-500"></i>
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div>
                        </div>
                    </div>
                    </div>
                    </ComPlaceholder>
                    </div>
                    

</template>

<script setup>
    import {ref,inject } from "@/plugin"
    const props = defineProps({
        notes:Object
    })
    const gv = inject('$gv');
    const emit = defineEmits(["onViewDetail", "onEdit","onPin"])

    function onViewDetail(note) {
        emit("onViewDetail",note)
    } 
    
    function onEdit(note) {
        emit("onEdit",note)
    } 
    function onPin(note) {
        emit("onPin",note)
    } 

</script>