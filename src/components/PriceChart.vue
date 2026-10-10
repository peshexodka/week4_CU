<script setup>
import { computed, ref, watch } from 'vue'
import ChartTooltip from './ChartTooltip.vue'
import { useChartWidth } from './useChartWidth.js'
const props = defineProps({ data: Array })
const hover = ref(null)
const { plot, width } = useChartWidth(900)
const points = computed(() => { const vals = props.data.filter(x => x.price !== null).map(x => x.price); const max = Math.max(...vals, 1); const min = Math.min(...vals, 0); return props.data.map((p, i) => ({ ...p, x: 10 + i * ((width.value - 20) / Math.max(props.data.length - 1, 1)), y: 145 - ((p.price || min) - min) / Math.max(max - min, 1) * 120 })) })
watch(points, () => { hover.value = null })
const segments = computed(() => {
  const result = []
  let segment = []
  for (const point of points.value) {
    if (point.price === null) { if (segment.length) result.push(segment); segment = [] }
    else segment.push(point)
  }
  if (segment.length) result.push(segment)
  return result
})
</script>
<template>
  <div class="price-chart">
    <div class="chart-title"><b>Цена в совершённых покупках</b><span>сентябрь 2024 — август 2026</span></div>
    <div ref="plot" class="chart-plot" @mouseleave="hover = null" @keydown.esc="hover = null">
      <svg :viewBox="`0 0 ${width} 180`" aria-label="Цена в совершённых покупках">
        <path v-for="(segment, index) in segments" :key="index" :d="segment.map((p, i) => `${i ? 'L' : 'M'}${p.x},${p.y}`).join(' ')" class="line" />
        <template v-for="p in points" :key="p.month">
          <circle v-if="p.price !== null" :cx="p.x" :cy="p.y" r="3" class="chart-point" />
          <ellipse
            v-if="p.price !== null" :cx="p.x" :cy="p.y" :rx="Math.min(13, (width - 20) / Math.max(data.length - 1, 1) / 2)" ry="13" class="chart-hit"
            tabindex="0" role="button" :aria-label="`${p.month}: ${Math.round(p.price).toLocaleString('ru-RU')} ₽`"
            @mouseenter="hover = p" @click="hover = p" @focus="hover = p" @blur="hover = null"
            @keydown.enter="hover = p" @keydown.space.prevent="hover = p"
          />
        </template>
      </svg>
      <ChartTooltip :point="hover" :width="width" :height="180" :month="hover?.month || ''" :value="hover ? `${Math.round(hover.price).toLocaleString('ru-RU')} ₽` : ''" />
    </div>
    <div class="chart-labels"><span>сен 2024</span><span>сен 2025</span><span>авг 2026</span></div>
  </div>
</template>
