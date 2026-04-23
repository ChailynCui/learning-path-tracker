# Changelog

该项目的更新记录维护在此文件中。
最后更新日期：2026-04-23

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，并遵循语义化版本（SemVer）。

## [Unreleased]

## [0.1.0] - 2026-04-23

### Added
- 支持在学习路线创建后继续追加章节。
- 新增接口 `POST /api/paths/{path_id}/units`。
- 路线详情页新增“追加章节”输入区（每行一个章节）。
- 前端新增 `appendPathUnits` API 调用封装。

### Changed
- 追加章节后会自动刷新章节列表与总章节数。
- 已完成路线在追加章节后会自动恢复为“进行中”状态，便于继续学习。

## [0.0.1] - 2026-04-22

### Added
- 初始化 Learning Path Tracker 项目，完成前后端基础结构搭建。
- 支持手动输入章节清单创建学习路线，默认按 `1 chapter/day` 生成计划。
- 提供 Dashboard、路线详情页与归档管理页。
- 支持学习计时器，以及开始、暂停、继续、结束后的学习时长记录。
- 支持章节完成打卡、待复习标记与复习完成记录。
- 支持周目标统计与 JSON 备份恢复能力。
