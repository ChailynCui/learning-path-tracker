<template>
  <section class="panel-card panel">
    <div class="head">
      <h3>学习状态区</h3>
      <p>看整体进展，也看本周学习节奏。</p>
    </div>

    <div class="progress-wrap">
      <div class="progress-title">
        <strong>{{ completionRate }}%</strong>
        <span>完成率</span>
      </div>
      <div class="meter" role="progressbar" :aria-valuenow="completionRate" aria-valuemin="0" aria-valuemax="100">
        <div class="meter-fill" :style="{ width: `${completionRate}%` }" />
      </div>
      <div class="summary">
        <span class="chip">已完成 {{ completedUnits }} 章</span>
        <span class="chip">待学习 {{ pendingUnits }} 章</span>
        <span class="chip">待复习 {{ pendingReview }} 章</span>
      </div>
    </div>

    <div class="grid">
      <article class="stat">
        <span class="label">本周学习时长</span>
        <strong>{{ weeklyMinutes }}</strong>
        <small>分钟</small>
      </article>
      <article class="stat">
        <span class="label">本周完成章节</span>
        <strong>{{ weeklyCompleted }}</strong>
        <small>章</small>
      </article>
      <article class="stat">
        <span class="label">待复习章节</span>
        <strong>{{ pendingReview }}</strong>
        <small>章</small>
      </article>
      <article class="stat">
        <span class="label">连续学习天数</span>
        <strong>{{ streak }}</strong>
        <small>天</small>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  weeklyMinutes: { type: Number, default: 0 },
  weeklyCompleted: { type: Number, default: 0 },
  pendingReview: { type: Number, default: 0 },
  streak: { type: Number, default: 0 },
  totalUnits: { type: Number, default: 0 },
  completedUnits: { type: Number, default: 0 }
});

const safeTotal = computed(() => Math.max(props.totalUnits, 1));
const completionRate = computed(() =>
  Math.round((Math.max(props.completedUnits, 0) / safeTotal.value) * 100)
);
const pendingUnits = computed(() =>
  Math.max(props.totalUnits - props.completedUnits, 0)
);
</script>

<style scoped>
.panel {
  padding: 18px;
  background: linear-gradient(160deg, rgba(15, 118, 110, 0.08), rgba(255, 255, 255, 0.96));
}

.head {
  margin-bottom: 14px;
}

h3 {
  margin: 0;
}

p {
  margin: 6px 0 0;
  color: var(--muted);
}

.progress-wrap {
  border: 1px solid rgba(25, 52, 65, 0.12);
  border-radius: 14px;
  padding: 14px 14px 12px;
  background: rgba(255, 255, 255, 0.8);
  margin-bottom: 14px;
}

.progress-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 10px;
}

.progress-title strong {
  font-family: "Space Grotesk", sans-serif;
  font-size: 36px;
  line-height: 1;
}

.progress-title span {
  color: var(--muted);
  font-size: 14px;
}

.summary {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meter {
  position: relative;
  height: 12px;
  border-radius: 999px;
  background: rgba(16, 42, 58, 0.12);
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #0f766e 0%, #13b29e 100%);
  box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.25);
  transition: width 0.35s ease;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 13px;
  color: var(--muted);
  border: 1px solid rgba(25, 52, 65, 0.14);
  background: rgba(255, 255, 255, 0.74);
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 10px;
}

.stat {
  border: 1px solid rgba(25, 52, 65, 0.12);
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.88);
}

.label {
  display: block;
  color: var(--muted);
  font-size: 13px;
}

.stat strong {
  display: block;
  margin-top: 6px;
  font-family: "Space Grotesk", sans-serif;
  font-size: 32px;
  line-height: 1;
}

small {
  color: var(--muted);
}

@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
