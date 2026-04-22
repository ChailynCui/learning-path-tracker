<template>
  <section class="panel-card panel">
    <div class="head">
      <div>
        <h3>学习记录</h3>
        <p>按天回看学习轨迹，避免重复信息。</p>
      </div>
      <div class="summary" v-if="logs.length">
        <span>累计</span>
        <strong>{{ totalMinutes }}</strong>
        <small>分钟</small>
        <span class="summary-sep">·</span>
        <strong>{{ logs.length }}</strong>
        <small>条记录</small>
      </div>
    </div>

    <div v-if="logs.length === 0" class="empty">完成章节后，这里会自动沉淀学习轨迹。</div>

    <div v-else class="day-groups">
      <section v-for="group in groupedLogs" :key="group.dateKey" class="group-card">
        <div class="group-head">
          <h4>{{ group.label }}</h4>
          <span>{{ group.totalMinutes }} 分钟 · {{ group.items.length }} 条</span>
        </div>

        <ul class="timeline">
          <li v-for="(log, idx) in group.items" :key="log.id" class="item">
            <div class="dot" />
            <div class="content">
              <div class="row">
                <strong>{{ log.unit_title || "章节学习" }}</strong>
                <el-tag size="small" effect="light" :type="isReviewLog(log) ? 'warning' : 'success'">
                  {{ isReviewLog(log) ? "复习" : "完成" }}
                </el-tag>
              </div>
              <p v-if="displayComment(log)" class="comment">{{ displayComment(log) }}</p>
              <div class="meta">
                <span>{{ log.study_minutes }} 分钟</span>
                <span class="meta-divider" />
                <span>第 {{ idx + 1 }} 条</span>
              </div>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  logs: { type: Array, default: () => [] }
});

const totalMinutes = computed(() =>
  props.logs.reduce((sum, item) => sum + (item.study_minutes || 0), 0)
);

const formatDate = (value) => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).format(date);
};

const normalizeText = (value) => (value || "").trim();

const isReviewLog = (log) => normalizeText(log.comment).includes("复习");

const displayComment = (log) => {
  const comment = normalizeText(log.comment);
  const title = normalizeText(log.unit_title);
  if (!comment) return "";
  if (title && comment === `${title} 已完成`) return "";
  if (title && comment === `复习完成：${title}`) return "";
  return comment;
};

const groupedLogs = computed(() => {
  const groups = [];
  const map = new Map();
  props.logs.forEach((log) => {
    const key = log.log_date || "unknown";
    if (!map.has(key)) {
      const group = {
        dateKey: key,
        label: formatDate(log.log_date),
        totalMinutes: 0,
        items: []
      };
      map.set(key, group);
      groups.push(group);
    }
    const group = map.get(key);
    group.items.push(log);
    group.totalMinutes += log.study_minutes || 0;
  });
  return groups;
});
</script>

<style scoped>
.panel {
  padding: 18px;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

h3 {
  margin: 0;
}

p {
  margin: 6px 0 0;
  color: var(--muted);
}

.summary {
  display: flex;
  align-items: baseline;
  gap: 6px;
  justify-content: flex-end;
  color: var(--muted);
  font-size: 14px;
  white-space: nowrap;
}

.summary strong {
  color: var(--ink);
  font-family: "Space Grotesk", sans-serif;
  font-size: 24px;
  line-height: 1;
}

.summary small {
  color: var(--muted);
  font-size: 13px;
}

.summary-sep {
  margin: 0 2px;
  color: rgba(79, 101, 114, 0.55);
}

.day-groups {
  display: grid;
  gap: 12px;
}

.group-card {
  border: 1px solid rgba(25, 52, 65, 0.12);
  border-radius: 14px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.82);
}

.group-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 10px;
}

h4 {
  margin: 0;
  font-size: 17px;
}

.group-head span {
  color: var(--muted);
  font-size: 13px;
}

.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.item {
  display: grid;
  grid-template-columns: 14px 1fr;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-top: 8px;
  background: var(--brand);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.2);
}

.content {
  border: 1px solid rgba(25, 52, 65, 0.09);
  border-radius: 12px;
  padding: 10px 12px 9px;
  background: rgba(255, 255, 255, 0.9);
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.comment {
  margin-top: 8px;
  color: var(--ink);
  line-height: 1.5;
}

.meta {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--muted);
  font-size: 13px;
}

.meta-divider {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: rgba(79, 101, 114, 0.4);
}

.empty {
  color: var(--muted);
  padding: 10px 0;
}

@media (max-width: 720px) {
  .head {
    flex-direction: column;
  }
  .summary {
    justify-content: flex-start;
    white-space: normal;
  }
  .group-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
