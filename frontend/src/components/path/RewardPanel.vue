<template>
  <section class="panel-card panel">
    <div class="head">
      <h3>激励区</h3>
      <span class="level-pill">Lv.{{ level }}</span>
    </div>
    <p class="sub">连续学习 {{ streak }} 天，今天继续推进就能保持节奏。</p>

    <div class="xp-row">
      <div>
        <strong>{{ xp }}</strong>
        <span>当前 XP</span>
      </div>
      <div>
        <strong>{{ nextGap }}</strong>
        <span>距下一级</span>
      </div>
    </div>
    <el-progress :percentage="progressToNext" :stroke-width="12" />

    <div class="badges">
      <span class="badge on">初学者</span>
      <span class="badge" :class="{ on: streak >= 3 }">稳定推进</span>
      <span class="badge" :class="{ on: streak >= 7 }">学习连击</span>
      <span class="badge" :class="{ on: level >= 3 }">稳态成长</span>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  level: { type: Number, default: 1 },
  xp: { type: Number, default: 0 },
  streak: { type: Number, default: 0 },
  nextGap: { type: Number, default: 0 }
});

const levels = [0, 50, 120, 250, 400];
const progressToNext = computed(() => {
  if (props.level >= 5) return 100;
  const currentThreshold = levels[Math.max(props.level - 1, 0)] ?? 0;
  const nextThreshold = levels[props.level] ?? 400;
  const span = Math.max(nextThreshold - currentThreshold, 1);
  const currentProgress = props.xp - currentThreshold;
  return Math.max(0, Math.min(Math.round((currentProgress / span) * 100), 100));
});
</script>

<style scoped>
.panel {
  padding: 18px;
  background: linear-gradient(145deg, rgba(15, 118, 110, 0.08), rgba(255, 255, 255, 0.92));
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

h3 {
  margin: 0;
}

.level-pill {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--brand);
  color: white;
}

.sub {
  margin: 0 0 12px;
  color: var(--muted);
}

.xp-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}

.xp-row div {
  border: 1px solid rgba(25, 52, 65, 0.12);
  border-radius: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.75);
}

.xp-row strong {
  display: block;
  font-size: 24px;
  font-family: "Space Grotesk", sans-serif;
}

.xp-row span {
  color: var(--muted);
  font-size: 13px;
}

.badges {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.badge {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(25, 52, 65, 0.14);
  color: var(--muted);
  background: rgba(255, 255, 255, 0.75);
  font-size: 13px;
}
.badge.on {
  color: white;
  background: var(--brand);
  border-color: var(--brand);
}
</style>
