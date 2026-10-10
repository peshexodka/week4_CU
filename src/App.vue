<script setup>
import { computed, ref, watch } from 'vue'
import * as d3 from 'd3'
import data from './data/purchases.json'
import Chart from './components/Chart.vue'
import PriceChart from './components/PriceChart.vue'

const rows = data.rows
const selectedMonth = ref('2026-08')
const period = ref('month')
const metric = ref('spend')
const limit = ref(10)
const search = ref('')
const selectedCategories = ref([])
const selectedProduct = ref(null)
const activeProduct = ref(null)

const money = value => `${Math.round(value || 0).toLocaleString('ru-RU')} ₽`
const number = value => Math.round(value || 0).toLocaleString('ru-RU')
const percent = value => `${(value || 0).toFixed(1).replace('.', ',')}%`
const monthNames = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
const monthLabel = value => { const [year, month] = value.split('-'); return `${monthNames[Number(month) - 1]} ${year}` }
const monthShort = value => d3.timeFormat('%b')(new Date(`${value}-01`)).replace('.', '')
const periodTitle = computed(() => period.value === 'month' ? `Выбранный месяц: ${monthLabel(selectedMonth.value)}` : period.value === '24' ? 'Последние 24 месяца' : 'Весь период')
const isService = row => row.c === 'Услуги Лавки'
const months = Array.from({ length: 24 }, (_, i) => d3.utcFormat('%Y-%m')(d3.utcMonth.offset(new Date('2024-09-01'), i)))
const allMonths = [...new Set(rows.map(r => r.d.slice(0, 7)))].sort()
const categories = computed(() => [...new Set(rows.map(r => r.c))].sort((a, b) => a.localeCompare(b, 'ru')))

function toggleCategory(category) {
  selectedCategories.value = selectedCategories.value.includes(category)
    ? selectedCategories.value.filter(x => x !== category) : [...selectedCategories.value, category]
}
function openProduct(item) {
  activeProduct.value = item
  selectedProduct.value = item.name
}
function closeProduct() {
  activeProduct.value = null
  selectedProduct.value = null
}
watch([period, search, selectedCategories, selectedMonth], closeProduct)
function scopedRows(forPeriod = period.value) {
  let result = rows
  if (selectedCategories.value.length) result = result.filter(r => selectedCategories.value.includes(r.c))
  if (forPeriod === 'month') result = result.filter(r => r.d.slice(0, 7) === selectedMonth.value)
  if (forPeriod === '24') result = result.filter(r => months.includes(r.d.slice(0, 7)))
  return result
}
function summarize(items) {
  const goods = items.filter(r => !isService(r))
  return {
    orders: new Set(items.map(r => r.o)).size, spend: d3.sum(items, r => r.s), goodsSpend: d3.sum(goods, r => r.s),
    quantity: d3.sum(goods, r => r.q), savings: d3.sum(goods, r => r.x * r.q), base: d3.sum(goods, r => r.b * r.q),
    discount: d3.sum(goods, r => r.x * r.q) / (d3.sum(goods, r => r.b * r.q) || 1) * 100, serviceSpend: d3.sum(items.filter(isService), r => r.s)
  }
}
const summary = computed(() => summarize(scopedRows('month')))
const previousSummary = computed(() => {
  const previous = d3.utcFormat('%Y-%m')(d3.utcMonth.offset(new Date(`${selectedMonth.value}-01`), -1))
  return summarize(scopedRows('month').filter(() => false).concat(rows.filter(r => r.d.slice(0, 7) === previous && (!selectedCategories.value.length || selectedCategories.value.includes(r.c)))))
})
function delta(current, previous, pp = false) { const change = pp ? current - previous : previous ? (current - previous) / previous * 100 : 0; return `${change >= 0 ? '+' : ''}${change.toFixed(pp ? 1 : 0).replace('.', ',')}${pp ? ' п.п.' : '%'}` }

const history = computed(() => months.map(month => {
  const s = summarize(rows.filter(r => r.d.slice(0, 7) === month && (!selectedCategories.value.length || selectedCategories.value.includes(r.c))))
  return { month, ...s }
}))
const periodRows = computed(() => scopedRows(period.value))
const ranking = computed(() => {
  const map = new Map()
  for (const r of periodRows.value.filter(r => !isService(r))) {
    if (!map.has(r.n)) map.set(r.n, { name: r.n, category: r.c, quantity: 0, spend: 0, orders: new Set(), byMonth: new Map() })
    const item = map.get(r.n); item.quantity += r.q; item.spend += r.s; item.orders.add(r.o)
    const m = r.d.slice(0, 7); item.byMonth.set(m, (item.byMonth.get(m) || { spend: 0, quantity: 0 }))
    item.byMonth.get(m).spend += r.s; item.byMonth.get(m).quantity += r.q
  }
  return [...map.values()].map(x => ({ ...x, orders: x.orders.size })).filter(x => x.name.toLowerCase().includes(search.value.toLowerCase())).sort((a, b) => b[metric.value] - a[metric.value]).slice(0, limit.value)
})
const categoryRows = computed(() => {
  const items = scopedRows(period.value); const total = d3.sum(items, r => r.s) || 1
  return categories.value.map(category => { const categoryItems = items.filter(r => r.c === category); const s = summarize(categoryItems); return { category, spend: s.spend, share: s.spend / total * 100, quantity: s.quantity, orders: s.orders, discount: s.discount } }).sort((a, b) => b.spend - a.spend || a.category.localeCompare(b.category, 'ru'))
})
const selectedProductData = computed(() => selectedProduct.value ? ranking.value.find(x => x.name === selectedProduct.value) : null)
const productHistory = computed(() => {
  if (!selectedProduct.value) return []
  return months.map(month => { const found = rows.filter(r => r.n === selectedProduct.value && r.d.slice(0, 7) === month && !isService(r) && (!selectedCategories.value.length || selectedCategories.value.includes(r.c))); const q = d3.sum(found, r => r.q); return { month, price: q ? d3.sum(found, r => r.s) / q : null } })
})
</script>

<template>
  <main class="page">
    <header class="hero"><div><p class="eyebrow">Личная аналитика покупок</p><h1>Дом и дача — история покупок</h1><p class="muted">Данные по 29 августа 2026 · доставленные заказы</p></div><div class="header-note">Адреса и точное время заказов<br>не публикуются</div></header>

    <section class="panel controls"><label>Месяц обзора<select v-model="selectedMonth"><option v-for="m in allMonths.slice(-24)" :key="m" :value="m">{{ monthLabel(m) }}</option></select></label><div class="filter-hint">Период графиков: сентябрь 2024 — август 2026</div></section>
    <section><div class="section-heading"><div><p class="eyebrow">01 · Обзор</p><h2>{{ monthLabel(selectedMonth) }}</h2></div><span class="period-caption">{{ selectedCategories.length ? 'С учётом выбранных категорий' : 'Все категории' }}</span></div><div class="cards"><article class="card"><span>Количество заказов</span><strong>{{ number(summary.orders) }}</strong><small>к предыдущему месяцу <b>{{ delta(summary.orders, previousSummary.orders) }}</b></small></article><article class="card"><span>Сумма трат</span><strong>{{ money(summary.spend) }}</strong><small>к предыдущему месяцу <b>{{ delta(summary.spend, previousSummary.spend) }}</b></small></article><article class="card"><span>Средняя скидка</span><strong>{{ percent(summary.discount) }}</strong><small>к предыдущему месяцу <b>{{ delta(summary.discount, previousSummary.discount, true) }}</b></small></article></div><p class="method">Средняя скидка — взвешенный процент: сумма экономии / сумма стоимости товаров до скидок × 100%. Услуги включены в траты, но не в скидку и количество товаров.</p></section>

    <section class="panel"><div class="section-heading"><div><p class="eyebrow">02 · Динамика за последние 24 месяца</p><h2>История покупок</h2></div><span class="legend-dot">Выбранный месяц: {{ monthLabel(selectedMonth) }}</span></div><div class="charts"><Chart title="Количество заказов" :data="history" field="orders" :selected="selectedMonth" format="number"/><Chart title="Траты, ₽" :data="history" field="spend" :selected="selectedMonth" format="money"/><Chart title="Скидка, %" :data="history" field="discount" :selected="selectedMonth" format="percent"/></div></section>

    <section class="panel"><div class="section-heading"><div><p class="eyebrow">03 · Рейтинг товаров</p><h2>Что покупали чаще</h2></div><div class="segmented"><button :class="{active: metric === 'quantity'}" @click="metric = 'quantity'">Количество</button><button :class="{active: metric === 'spend'}" @click="metric = 'spend'">Траты</button></div></div><div class="toolbar"><label>Период<select v-model="period"><option value="month">Выбранный месяц</option><option value="24">Последние 24 месяца</option><option value="all">Весь период</option></select></label><label>Показать<select v-model.number="limit"><option :value="10">Топ-10</option><option :value="20">Топ-20</option></select></label><label class="search">Поиск по названию<input v-model="search" type="search" placeholder="Например, молоко" /></label></div><div class="ranking"><button v-for="(item, i) in ranking" :key="item.name" class="rank-row" @click="openProduct(item)" @mouseenter="openProduct(item)" @focus="openProduct(item)"><span class="rank-num">{{ i + 1 }}</span><span class="product-icon" aria-hidden="true">▦</span><span class="rank-name"><b>{{ item.name }}</b><small>{{ item.category }} · {{ number(item.quantity) }} шт.</small></span><span class="bar-wrap"><i :style="{width: `${(item[metric] / (ranking[0]?.[metric] || 1)) * 100}%`}"></i></span><strong>{{ metric === 'quantity' ? number(item.quantity) + ' шт.' : money(item.spend) }}</strong></button><p v-if="!ranking.length" class="empty">За выбранный период покупок не найдено.</p></div></section>

    <section v-if="activeProduct" class="panel product-detail"><div class="section-heading"><div><p class="eyebrow">04 · Подсказка о товаре</p><h2>{{ activeProduct.name }}</h2><p class="muted">{{ activeProduct.category }} · Цена в совершённых покупках</p></div><button class="close" @click="closeProduct">Закрыть</button></div><div class="detail-stats"><span><b>{{ number(activeProduct.quantity) }}</b> куплено</span><span><b>{{ money(activeProduct.spend) }}</b> траты</span><span><b>{{ number(activeProduct.orders) }}</b> заказов с товаром</span></div><PriceChart :data="productHistory"/></section>

    <section class="panel"><div class="section-heading"><div><p class="eyebrow">05 · Категории</p><h2>Структура расходов</h2><p class="muted">{{ periodTitle }}</p></div><button v-if="selectedCategories.length" class="reset" @click="selectedCategories = []">Сбросить фильтр</button></div><div class="category-layout"><div class="category-list"><button v-for="item in categoryRows" :key="item.category" :class="{chosen: selectedCategories.includes(item.category)}" class="category-row" @click="toggleCategory(item.category)"><span class="check">{{ selectedCategories.includes(item.category) ? '✓' : '' }}</span><span><b>{{ item.category }}</b><small>{{ percent(item.share) }} расходов</small></span><strong>{{ money(item.spend) }}</strong><small>{{ number(item.quantity) }} шт. · {{ number(item.orders) }} заказов · скидка {{ percent(item.discount) }}</small></button></div><div class="category-summary"><div><span>Траты за период</span><b>{{ money(summarize(periodRows).spend) }}</b></div><div><span>Услуги Лавки</span><b>{{ money(summarize(periodRows).serviceSpend) }}</b></div><p>Один заказ может содержать несколько категорий, поэтому количества заказов по категориям нельзя складывать. Доли рассчитаны от общих трат выбранного периода, включая услуги. Средняя скидка категории считается только по товарам.</p></div></div></section>
    <footer><span>Источник: датасет «Дом и дача», вариант A</span><span>Визуализация без серверной части · товары без изображений Items</span></footer>
  </main>
</template>
