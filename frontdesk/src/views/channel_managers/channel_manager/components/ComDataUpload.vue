<template>
  <div class="box">
    <div class="flex justify-content-between">
      <div>
        <div class="icon blue">
          <ComIcon :icon="Icon" height="30px" />
        </div>
        <span>{{ $t(Title) }}</span>
        <div>
          <span class="text-5xl font-bold">{{ value || 0 }}</span>
        </div>
        <small class="color-orange">{{$t(controlStatus)}}</small>
      </div>
      <div class="flex justify-end align-items-end">
        <Button class="bg-transparent border-none border-blue-500 text-blue-500 p-0 hover:bg-transparent">
          {{$t('View')}}
        </Button>
      </div>
    </div>
  </div>
</template>
<script setup> 


const props = defineProps({
  Title: String,
  Icon: String,
  value: [String, Number],
  controlStatus: String
})
</script>
<style scoped>
.box {
  flex: 1;
  background: #fafafa;
  border-radius: 14px;
  padding: 20px;
  border: 1px solid #eee;
  transition: 0.2s;
}

.box:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.box span {
  font-size: 12px;
  color: #9ca3af;
}

.box h3 {
  margin: 5px 0 0;
}

/* Icons */
.icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  font-size: 20px;
}

.blue {
  background: #dbeafe;
}
</style>