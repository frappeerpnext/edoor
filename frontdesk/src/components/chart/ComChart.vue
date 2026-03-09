<template>

  <v-chart class="chart" :style="{ height: height }" :option="option" autoresize />
</template>

<script setup>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, defineProps } from 'vue';

// Import necessary ECharts components
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// Define props for chart data
const props = defineProps({
  chartData: Object,
  height:{
    default:'350px',
    type:String
  }
});

// Reactive option for the chart
const option = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow', // Use shadow for bar chart
    },
  },
  legend: props.chartData?.legend ||  {
    orient: 'horizontal',
    itemGap: 10, // Increase spacing between legend items if needed
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: props.chartData.labels, // Set initial labels
  },
  yAxis: {
    type: 'value',
  },
  series: props.chartData.datasets, // Set initial datasets
});

// Watch for changes in the chartData prop
watch(
  () => props.chartData,
  (newChartData) => {
    // Update the chart options when chartData changes
    option.value = {
      ...option.value, // Keep the existing options
      xAxis: {
        ...option.value.xAxis,
        data: newChartData.labels, // Update labels when they change
      },
      series: newChartData.datasets, // Update series data when it changes
    };
  },
  { deep: true } // Watch deeply for changes in nested objects
);
</script>


