<script setup>
import { computed, ref, watch } from 'vue'
import ChartTooltip from './ChartTooltip.vue'
import { useChartWidth } from './useChartWidth.js'
const props = defineProps({ title: String, data: Array, field: String, selected: String, format: String })
const hover = ref(null)
const { plot, width } = useChartWidth(640)
const points = computed(() => { const vals = props.data.map(x => +x[props.field] || 0); const max = Math.max(...vals, 1); return props.data.map((p, i) => ({ ...p, value: vals[i], x: 34 + i * ((width.value - 44) / Math.max(props.data.length - 1, 1)), y: 150 - vals[i] / max * 130 })) })
watch(points, () => { hover.value = null })
const path = computed(() => points.value.map((p, i) => `${i ? 'L' : 'M'}${p.x},${p.y}`).join(' '))
const display = value => props.format === 'money' ? `${Math.round(value).toLocaleString('ru-RU')} ₽` : props.format === 'percent' ? `${value.toFixed(1).replace('.', ',')}%` : Math.round(value).toLocaleString('ru-RU')
const label = value => { const names = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']; const [year, month] = value.split('-'); return `${names[Number(month) - 1]} ${year}` }
</script>
<template>
  <div class="chart">
    <div class="chart-title"><b>{{ title }}</b><span>{{ label(data[data.length - 1]?.month) }}</span></div>
    <div ref="plot" class="chart-plot" @mouseleave="hover = null" @keydown.esc="hover = null">
      <svg :viewBox="`0 0 ${width} 190`" :aria-label="title">
        <line x1="34" y1="10" x2="34" y2="155" class="axis" />
        <line x1="34" y1="155" :x2="width - 10" y2="155" class="axis" />
        <path :d="path" class="line" />
        <circle v-for="p in points" :key="p.month" :cx="p.x" :cy="p.y" :r="p.month === selected ? 5 : 2.5" class="chart-point" :class="{selected: p.month === selected}" />
        <ellipse
          v-for="p in points" :key="`hit-${p.month}`" :cx="p.x" :cy="p.y" :rx="Math.min(13, (width - 44) / Math.max(data.length - 1, 1) / 2)" ry="13" class="chart-hit"
          tabindex="0" role="button" :aria-label="`${title}, ${label(p.month)}: ${display(p.value)}`"
          @click="hover = p" @mouseenter="hover = p" @focus="hover = p" @blur="hover = null"
          @keydown.enter="hover = p" @keydown.space.prevent="hover = p"
        />
      </svg>
      <ChartTooltip :point="hover" :width="width" :height="190" :month="hover ? label(hover.month) : ''" :value="hover ? display(hover.value) : ''" />
    </div>
    <div class="chart-labels"><span>{{ label(data[0]?.month) }}</span><span>{{ label(data[Math.floor(data.length / 2)]?.month) }}</span><span>{{ label(data[data.length - 1]?.month) }}</span></div>
  </div>
</template>
