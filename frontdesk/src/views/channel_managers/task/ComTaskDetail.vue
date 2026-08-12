<template>
    <!-- <div>
        CM Task Detail
        {{ doc }}
        
    </div> -->


    <div class="flex gap-2 align-items-center">
        <div>
            <Avatar :label="avatar_letter" size="large"
                style="background-color: #ece9fc; color: #2a1261;border-radius: 50% !important;" shape="circle" />
        </div>
        <div>
            <div><strong>{{ doc?.modified_by }}</strong></div>
            <i>
                <ComTimeago :date='doc?.modified' />
            </i>
        </div>
    </div>
    <br />
    <hr />
    <div class="task-card">
        <div class="card-body">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">{{ $t('Due Date') }}</div>
                    <div class="info-value">{{ moment(doc?.date).format('DD-MM-yyyy') || '—' }}</div>
                </div>
                <div class="info-item">
                    
                    <div class="info-label">{{ $t('Priority') }}</div>
                    <div class="info-value">{{ doc?.priority }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">{{ $t('Subject') }}</div>
                    <div class="info-value light-meta">{{ doc?.custom_subject || '—' }}</div>
                </div>
                <div class="info-item">
                  
                </div>
                <div class="info-item">
                    <div class="info-label">{{ $t('Status') }}</div>
                    <div class="info-value">
                        <Tag class="border-round" severity="success" :value="doc?.status"></Tag>
                    </div>
                </div>
            </div>

            <div class="description-section">
                <div class="description-header">
                    <i class="pi pi-list"></i>
                    <h3>Todo</h3>
                </div>
                <div class="description-text" v-html="doc?.description"></div>
            </div>
            <div class="action-area">
                <Button class="border-0" label="Make as Complete" @click="onComplete"
                    :disabled="doc?.status != 'Open'" />
            </div>

        </div>
    </div>
</template>
<script setup>
import Tag from 'primevue/tag';
import { inject, onMounted, ref } from "vue"
const dialogRef = inject("dialogRef");
const doc = ref()
const moment = inject("$moment")
const avatar_letter = ref('')
async function onComplete() {
    const l = await window.showLoading()
    const res = await app.setValue("ToDo", doc.value.name, "status", "Closed")
    if (res.data) {
        doc.value = res.data
    }
    l.close()

}
onMounted(async () => {

    const res = await app.getDoc("ToDo", dialogRef.value.data.docname)
    if (res.data) {
        doc.value = res.data
        avatar_letter.value = doc.value.modified_by.charAt(0).toUpperCase()
        console.log(doc.value)
    }
})

const getPlainText = (html) => {
    const temp = document.createElement('div')
    temp.innerHTML = html
    return temp.textContent || temp.innerText || ''
}
</script>
<style scoped>
.task-card {
    width: 100%;
    background: #ffffff;
    border-radius: 28px;
    overflow: hidden;
    transition: all 0.2s ease;
}

/* header area */
.card-header {
    padding: 22px 28px 16px 28px;
    border-bottom: 1px solid #eef2f6;
    display: flex;
    align-items: center;
    gap: 10px
}

.header-title-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.cm-badge {
    display: flex;
    align-items: center;
    gap: 8px;
}

.cm-badge i,
.icon-desc {
    color: #4f46e5;
    font-size: 18px;
    background: #eef2ff;
    padding: 6px;
    border-radius: 10px;
}

.cm-badge span {
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    color: #64748b;
}

.task-title {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.2;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-top: 4px;
}

.property-tag {
    display: inline-flex;
    align-items: center;
    background: #f1f5f9;
    padding: 6px 14px;
    border-radius: 40px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #334155;
    margin-top: 8px;
    width: fit-content;
    gap: 8px;
}

.property-tag i {
    color: #3b82f6;
    font-size: 13px;
}

.status-chip {
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-badge {
    background: #dcfce7;
    color: #15803d;
    font-weight: 600;
    font-size: 0.8rem;
    padding: 6px 14px;
    border-radius: 40px;
    display: flex;
    align-items: center;
    border: 1px solid #bbf7d0;
}

.priority-badge {
    background: #fef9c3;
    color: #854d0e;
    font-weight: 600;
    font-size: 0.8rem;
    padding: 6px 14px;
    border-radius: 40px;
    display: flex;
    align-items: center;
    gap: 6px;
    border: 1px solid #fde68a;
}

/* body grid */
.card-body {
    padding: 24px 28px 28px 28px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 18px 24px;
    margin-bottom: 28px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.info-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 6px;
}

.info-label i {
    font-size: 13px;
    width: 18px;
    color: #94a3b8;
}

.info-value {
    font-size: 1rem;
    font-weight: 500;
    color: #0f172a;
    background: #fafcff;
    padding: 8px 0;
    border-bottom: 1px dashed #e2e8f0;
    padding-left: 10px;
}

.info-value.light-meta {
    color: #475569;
    font-size: 0.9rem;
}

.allocated-placeholder {
    color: #94a3b8;
    font-style: italic;
    font-weight: 400;
}

/* description block */
.description-section {
    background: #f8fafc;
    border-radius: 20px;
    padding: 20px 22px;
    margin-bottom: 28px;
    border: 1px solid #eef2f6;
}

.description-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.description-header i {
    color: #4f46e5;
    background: #e0e7ff;
    padding: 6px;
    border-radius: 10px;
    font-size: 14px;
}

.description-header h3 {
    font-weight: 600;
    font-size: 1rem;
    color: #1e293b;
    letter-spacing: -0.01em;
}

.description-text {
    font-size: 1rem;
    line-height: 1.6;
    color: #1e293b;
    padding-left: 8px;
    border-left: 3px solid #cbd5e1;
    margin-left: 6px;
    padding-top: 4px;
    padding-bottom: 4px;
}

.description-text i {
    color: #64748b;
    margin-right: 6px;
}

/* meta timestamps */
.meta-footer {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid #eef2f6;
    padding-top: 22px;
    margin-bottom: 8px;
}

.timestamps {
    display: flex;
    gap: 20px;
    font-size: 0.8rem;
    color: #64748b;
}

.timestamps span {
    display: flex;
    align-items: center;
    gap: 6px;
}

.timestamps i {
    color: #94a3b8;
    font-size: 13px;
}

/* Action button */
.action-area {
    display: flex;
    justify-content: flex-end;
    margin-top: 8px;
}

.btn-complete {
    background: #0f172a;
    color: white;
    border: none;
    padding: 14px 32px;
    border-radius: 60px;
    font-weight: 600;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    box-shadow: 0 8px 16px -6px rgba(15, 23, 42, 0.2);
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid #1e293b;
    letter-spacing: -0.01em;
    width: fit-content;
}

.btn-complete i {
    font-size: 1.2rem;
    color: #a5b4fc;
    transition: transform 0.2s;
}

.btn-complete:hover {
    background: #1e293b;
    box-shadow: 0 12px 20px -8px rgba(15, 23, 42, 0.25);
    transform: translateY(-1px);
}

.btn-complete:active {
    transform: translateY(1px);
    box-shadow: 0 4px 10px -4px rgba(0, 0, 0, 0.2);
}

/* small extras */
.reference-meta {
    display: flex;
    gap: 12px;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 12px;
}

.reference-meta i {
    margin-right: 4px;
}
</style>