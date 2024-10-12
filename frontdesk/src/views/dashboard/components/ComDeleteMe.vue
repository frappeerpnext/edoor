<template>
    <v-chart class="chart" :option="option" autoresize />
  </template>
  
  <script setup>
  import { use } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { BarChart } from 'echarts/charts';
  import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
  } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { ref, provide } from 'vue';
  
  // Use the necessary ECharts components
  
  use([
    CanvasRenderer,
    BarChart, // Switched from PieChart to BarChart
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
  ]);
  

  // Define the chart options for a bar chart
  const option = ref({
    title: {
      text: 'Traffic Sources',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow', // Use shadow for bar chart
      },
    },
    legend: {
      orient: 'horizontal',
      top: 'bottom',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: ['Direct', 'Email', 'Ad Networks', 'Video Ads', 'Search Engines'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: 'Traffic Sources',
        type: 'bar', // Switched from pie to bar
        data: [335, 310, 234, 135, 1548], // Bar chart data array
        emphasis: {
          itemStyle: {
            color: '#ff9800',
          },
        },
      },
    ],
  });
  </script>
  
  <style scoped>
  .chart {
    height: 100vh;
  }
  </style>
  