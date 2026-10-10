<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ data: Array })
const hover = ref(null)
const points = computed(() => { const vals = props.data.filter(x => x.price !== null).map(x => x.price); const max = Math.max(...vals, 1); const min = Math.min(...vals, 0); return props.data.map((p, i) => ({ ...p, x: 10 + i * (880 / Math.max(props.data.length - 1, 1)), y: 145 - ((p.price || min) - min) / Math.max(max - min, 1) * 120 })) })
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
<template><div class="price-chart"><div class="chart-title"><b>Цена в совершённых покупках</b><span>сентябрь 2024 — август 2026</span></div><svg viewBox="0 0 900 180" preserveAspectRatio="none"><path v-for="(segment, index) in segments" :key="index" :d="segment.map((p, i) => `${i ? 'L' : 'M'}${p.x},${p.y}`).join(' ')" class="line"/><template v-for="p in points" :key="p.month"><circle v-if="p.price !== null" :cx="p.x" :cy="p.y" r="3" @mouseenter="hover = p" @click="hover = p"/></template><g v-if="hover"><rect :x="Math.min(hover.x + 7, 760)" :y="Math.max(hover.y - 40, 2)" width="120" height="34" rx="5" class="tip-bg"/><text :x="Math.min(hover.x + 14, 767)" :y="Math.max(hover.y - 20, 22)" class="tip-text">{{ hover.month }}</text><text :x="Math.min(hover.x + 14, 767)" :y="Math.max(hover.y - 7, 35)" class="tip-text">{{ Math.round(hover.price).toLocaleString('ru-RU') }} ₽</text></g></svg><div class="chart-labels"><span>сен 2024</span><span>сен 2025</span><span>авг 2026</span></div></div></template>
