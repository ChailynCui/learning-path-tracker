<template>
  <section class="panel-card panel">
    <div class="head">
      <h3>章节列表</h3>
      <span>{{ units.length }} 章</span>
    </div>

    <div class="table-shell">
      <el-table :data="units" style="width: 100%" stripe :row-class-name="rowClassName">
        <el-table-column label="章节" min-width="360">
          <template #default="scope">
            <div class="chapter-cell">
              <span class="order-pill">{{ scope.row.unit_order }}</span>
              <div class="chapter-main">
                <strong>{{ scope.row.unit_title }}</strong>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'done' ? 'success' : 'info'" effect="light" size="small">
              {{ scope.row.status === "done" ? "已完成" : "待学习" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="完成时间" width="180">
          <template #default="scope">
            <span class="time-text">{{ formatCompletedAt(scope.row.completed_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="本章计划" width="190">
          <template #default="scope">
            <div class="plan-cell">
              <el-input-number
                :model-value="scope.row.planned_days || 1"
                :min="1"
                :max="30"
                size="small"
                @change="(value) => $emit('plan-days', scope.row, Number(value) || 1)"
              />
              <span>天</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="复习" width="110">
          <template #default="scope">
            <el-tag v-if="scope.row.review_needed" type="warning" size="small">需复习</el-tag>
            <span v-else class="review-empty">无需</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <div class="actions">
              <el-button
                size="small"
                :disabled="scope.row.status === 'done'"
                @click="$emit('complete', scope.row)"
              >
                标记完成
              </el-button>
              <el-button
                v-if="scope.row.status === 'done' && !scope.row.review_needed"
                size="small"
                text
                @click="$emit('mark-review', scope.row)"
              >
                加入复习
              </el-button>
              <el-button
                v-if="scope.row.status === 'done' && scope.row.review_needed"
                size="small"
                text
                @click="$emit('review', scope.row)"
              >
                复习完成
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </section>
</template>

<script setup>
defineProps({
  units: { type: Array, default: () => [] }
});
defineEmits(["complete", "mark-review", "review", "plan-days"]);

const formatCompletedAt = (value) => {
  if (!value) return "-";
  if (typeof value === "string") {
    const matched = value.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})/);
    if (matched) {
      const [, year, month, day, hour, minute] = matched;
      return `${year}/${month}/${day} ${hour}:${minute}`;
    }
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(date);
};

const rowClassName = ({ row }) => {
  if (row.review_needed) return "row-review";
  if (row.status === "done") return "row-done";
  return "";
};
</script>

<style scoped>
.panel {
  padding: 16px 16px 18px;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}

h3 {
  margin: 0;
}

.head span {
  color: var(--muted);
  font-size: 13px;
}

.table-shell {
  border: 1px solid rgba(25, 52, 65, 0.1);
  border-radius: 14px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.82);
}

.chapter-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chapter-main {
  min-height: 28px;
  display: flex;
  align-items: center;
}

.chapter-main strong {
  font-size: 17px;
  line-height: 1.25;
}

.order-pill {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: "Space Grotesk", sans-serif;
  font-size: 13px;
  color: #0b5f58;
  border: 1px solid rgba(15, 118, 110, 0.3);
  background: rgba(15, 118, 110, 0.11);
}

.plan-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.plan-cell span {
  color: var(--muted);
  font-size: 12px;
}

.actions {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.time-text {
  color: var(--muted);
  font-size: 13px;
}

.review-empty {
  color: var(--muted);
  font-size: 13px;
}

:deep(.el-table) {
  --el-table-header-bg-color: rgba(15, 118, 110, 0.06);
  --el-table-row-hover-bg-color: rgba(15, 118, 110, 0.05);
  --el-table-tr-bg-color: transparent;
}

:deep(.el-table .row-done td.el-table__cell) {
  background: rgba(15, 118, 110, 0.035);
}

:deep(.el-table .row-review td.el-table__cell) {
  background: rgba(245, 158, 11, 0.05);
}

@media (max-width: 840px) {
  .chapter-main strong {
    font-size: 16px;
  }
}
</style>
