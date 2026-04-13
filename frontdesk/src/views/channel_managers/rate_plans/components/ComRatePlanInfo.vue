<template>
    <div class="grid p-5 m-0 flex justify-content-center">

        <!-- Basic Information -->
        <div class="col-6 card">
            <div class="card-inner ">
                <h3>{{$t('Rate Plan Info')}}</h3>

                <div class="form-row"> 
                    <div class="form-group" style="flex:1;"> 
                        <div class="status-box">
                            <div class="status-text">
                                <strong>{{$t('Rate Plan Status')}}</strong>
                                {{rateInfo.rate_type?.disabled==1? `${$t('Currently active and bookable')}`:`${$t('Currently inactive and unbookable')}`}}
                            </div>
                            <div class="switch" :class="rateInfo.rate_type?.disabled==1?'active':''"></div>
                        </div>
                    </div>
                </div>  
                <div class="form-row"> 
                    <div class="form-row">
                        <div class="form-group">
                            <label>{{$t('Rate Type')}}</label>
                            <InputText :value="rateInfo.rate_type?.name" readonly/>
                        </div> 
                    </div>
                    <div class="form-group">
                        <label>{{$t('Channel Rate Type')}}</label>
                        <InputText :value="rateInfo.cm_rate_plan_list?.rate_plan_name" readonly/>
                    </div>

                    <div class="form-group">
                        <label>{{ $t('Channel Rate Code') }}</label>
                        <InputText :value="rateInfo.cm_rate_plan_list?.cm_rate_plan" readonly/>
                    </div>
                </div>  
                <div class="form-row">
                    <div class="form-group" style="flex:1;">
                        <label>{{$t('Available Room Types')}}</label>
                        <div class="checkbox-group">
                            <div class="flex flex-column gap-4">
                                <template v-for="rt in rateInfo.rate_type?.room_types"> 
                                    <div class="flex gap-1">
                                        <Checkbox v-model="checked" :binary="true" :trueValue="1" :falseValue="0" @change="checked = 1"/> 
                                        <label >
                                            {{roomTypes
                                                .filter(name => name.edoor_room_type === rt.room_type)
                                                .map(name => name.room_type_name)
                                                .join('')
                                            }}
                                        </label> 
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div> 
                    <div class="form-group" style="flex:1;">
                        <label>{{$t('Available Business Source')}}</label>
                        <div class="checkbox-group">
                            <div class="flex flex-column gap-4">
                                <template v-for="bs in rateInfo.rate_type?.business_source"> 
                                    <div class="flex gap-1">
                                        <Checkbox v-model="checked" :binary="true" :trueValue="1" :falseValue="0" @change="checked = 1"/> 
                                        <label>
                                            {{bs.business_source}}
                                        </label> 
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div> 
                </div>

                <template v-for="date in rateInfo.room_rate_min_max_date">
                    <div class="form-group" style="flex:1">
                        <label>Sell Start Date</label>
                        <input :value="date.start_date" />
                    </div> 
                </template>
    
                <div class="form-group">
                    <label>{{$t('Note')}}</label>
                    <textarea readonly>{{ $t(`${rateInfo.rate_type?.note}`) }}</textarea>
                </div> 
            </div>
        </div>   
    </div>
    {{ rateInfo.room_rate_min_max_date }}
</template>
<script setup>
import { onMounted, ref } from 'vue';
import { useRatePlan } from '../hooks/useRatePlan'; 
import {i18n} from '@/i18n'; 
const { t: $t } = i18n.global;
const { 
        rateInfo, 
        roomTypes
    } = useRatePlan();    
const checked = ref(1)
onMounted(() => {    
    console.log(roomTypes)
})
</script>
<style scoped> 
.card .card-inner {
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}
 
.card h3 {
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}

.form-group {
    margin-bottom: 15px;
}

.form-row {
    display: flex;
    gap: 15px;
}

.form-group label {
    display: block;
    font-size: 12px;
    margin-bottom: 6px;
    color: #666;
    font-weight: 500;
}

input,
select,
textarea {
    width: 100%;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid #e0e4ef;
    background: #f9fafc;
    font-size: 14px;
    transition: 0.2s;
}

input:focus,
select:focus,
textarea:focus {
    outline: none;
    border-color: #6c63ff;
    background: #fff;
}

textarea {
    resize: none;
    height: 70px;
}

.checkbox-group {
    background: #f9fafc;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #e0e4ef;
}

.checkbox-group label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
}

.toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f9fafc;
    border: 1px solid #e0e4ef;
    padding: 10px 12px;
    border-radius: 10px;
}

.switch {
    width: 40px;
    height: 20px;
    background: #dcdff1;
    border-radius: 20px;
    position: relative;
    cursor: pointer;
}

.switch::after {
    content: '';
    width: 16px;
    height: 16px;
    background: white;
    position: absolute;
    top: 2px;
    left: 2px;
    border-radius: 50%;
    transition: 0.3s;
}

.switch.active {
    background: #6c63ff;
}

.switch.active::after {
    left: 22px;
}

.status-box {
    background: #eef0ff;
    border-radius: 12px;
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.status-text {
    font-size: 13px;
    color: #555;
}

.status-text strong {
    display: block;
    color: #333;
}

.small-row {
    display: flex;
    gap: 10px;
    align-items: center;
}

.multiplier {
    display: flex;
    align-items: center;
    gap: 8px;
}

.multiplier span {
    font-size: 18px;
    color: #888;
}
</style>