<template> 
    <div> 
        <div class="task-container">  
            <div class="task-list"> 
               <div v-if="data?.length > 0" v-for="d in data" @click="onViewLogDetail(d)" class="cursor-pointer">
  <div class="task-card open">
    <div class="w-full " :class="d.priority === 'High' ? 'border-button-color-danger' : 'border-button-color-warning'">
       <Tag class="border-round px-3" :severity="d.priority=='High'?'danger':'warning'">
        {{ d.priority }}
      </Tag> 
    </div>
     
    <div class="task-header">
      <span class="task-title">{{ d.custom_subject }}</span>
     
    </div>

    <div class="task-desc ellipsis">
      {{ getPlainText(d.description) }}
    </div> 
  </div> 
</div>
                <div v-else class="flex flex-column align-items-center w-full h-23rem justify-content-center">
                    <com-icon icon="iconTaskSquare" width="40px"/>
                    <div class="font-bold">{{$t('No Tasks')}}</div>
                    <div>{{$t(`There's no task for you`)}}</div>
                </div>
            </div> 

        </div>

    </div>
</template>
<script setup>

import Tag from 'primevue/tag';

const props = defineProps({
    data: Object
})
function onViewLogDetail(d) {
    app.dialog.viewChannelManagerTaskDetail("CM Task Detail - " + d.custom_subject, d.name)
}

const getPlainText = (html) => {
    const temp = document.createElement('div')
    temp.innerHTML = html
    return temp.textContent || temp.innerText || ''
}
</script>
<style scoped>
.task-container {  
    overflow: hidden; 
}

/* Tabs */
.tabs {
    display: flex;
    padding: 10px;
    gap: 8px;
}
.ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 2; /* change to 2,3,4 lines */
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tab {
    flex: 1;
    padding: 8px;
    border: none;
    border-radius: 20px;
    background: #eee;
    cursor: pointer;
    font-weight: 600;
}

.tab.active {
    background: #eab308;
    color: white;
}

/* Task List */
.task-list {
    max-height: 300px;
    overflow-y: auto; 
}

/* Card */
.task-card {
    background: #eef2ff;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
    /* border-left: 4px solid #f9d979; */
}

/* Header */
.task-header {
    display: flex;
    justify-content: space-between; 
}

.task-title {
    font-weight: 600;
}

.task-status {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 12px;
    background: #e0f2fe;
    color: #0284c7;
}

/* Description */
.task-desc {
    font-size: 13px;
    color: #555; 
}

/* Button */
.task-action {
    padding: 6px 10px;
    border: none;
    border-radius: 6px;
    background: #3b82f6;
    color: white;
    font-size: 12px;
    cursor: pointer;
}

.task-action:hover {
    background: #2563eb;
}

/* Footer */
.footer {
    padding: 10px;
    border-top: 1px solid #eee;
}

.view-all {
    width: 100%;
    padding: 10px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
}
</style>