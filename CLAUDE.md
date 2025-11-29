# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个使用 Pygame 构建的地牢探索游戏 (Dungeon Explorer)。玩家在随机生成的迷宫中探索，击杀怪物获取经验值升级，支持单人和双人模式。

## 安装与运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行游戏
python 001.py
```

依赖库（仅使用标准库 + pygame）：
- pygame
- random, math, json, time (标准库)

## 代码架构

### 文件结构
- `001.py` - 主游戏文件，包含所有游戏逻辑
- `graphics_enhancement.py` - 图形增强模块（粒子系统、光照系统、屏幕抖动）

### 核心系统

**主游戏循环** (`001.py`)
- 迷宫生成：使用深度优先搜索算法生成 150x150 格子的随机迷宫
- 玩家系统：支持双人模式，包含移动、技能、子弹射击
- 怪物系统：10种普通怪物 + 2种Boss，具有AI寻路和防卡墙机制
- 技能系统：5种技能（范围攻击、治疗、闪现、无敌、多重射击）
- 关卡系统：10个关卡，递增难度

**图形增强** (`graphics_enhancement.py`)
- `ParticleSystem` - 粒子效果（爆炸、击中效果、拖尾）
- `LightingSystem` - 动态光照系统，带渐变缓存优化
- `ScreenShake` - 屏幕抖动效果

### 关键类

| 类名 | 文件 | 用途 |
|------|------|------|
| `Monster` | 001.py | 怪物实体，包含AI移动和战斗逻辑 |
| `Bullet` | 001.py | 子弹实体 |
| `Weapon` | 001.py | 武器系统 |
| `HealthPack` | 001.py | 回血包 |
| `Camera` | 001.py | 摄像机跟随 |
| `Shop` | 001.py | 商店系统，用经验值购买物品 |
| `Dialogue` | 001.py | 对话系统 |
| `ParticleSystem` | graphics_enhancement.py | 粒子效果管理 |
| `LightingSystem` | graphics_enhancement.py | 光照效果管理 |
| `ScreenShake` | graphics_enhancement.py | 屏幕抖动效果 |

### 游戏常量

游戏平衡相关常量定义在 `001.py` 开头：
- `MAZE_WIDTH/MAZE_HEIGHT` - 迷宫尺寸 (150x150)
- `CELL_SIZE` - 单元格大小 (40像素)
- `MAX_MONSTERS` - 最大怪物数量 (150)
- `SKILLS` - 技能定义字典
- `BOSS_TYPES` - Boss类型定义
- `WEAPON_TYPES` - 武器类型定义
- `LEVELS` - 关卡配置

### 控制按键

- WASD / 方向键 - 移动
- 鼠标左键 - 射击
- Space - 范围攻击
- F - 治疗
- E - 闪现
- T - 无敌
- R - 多重射击
- Shift - 冲刺
- S - 打开/关闭商店
- 1/2/3 - 商店购买物品

## 可选资源文件

- `中国球.png` - 玩家图片（如不存在则使用默认图形）
- `game_save.txt` - 游戏存档文件（JSON格式，通过 `save_game()`/`load_game()` 函数管理）

## 游戏功能

- **迷宫生成**：深度优先搜索算法，150x150格子
- **怪物AI**：5格范围内追踪玩家，智能寻路防卡墙
- **商店系统**：用经验值购买血包和武器
- **存档系统**：保存玩家等级、经验、血量、武器等
- **双人模式**：`multiplayer_mode` 变量控制
- **穿墙模式**：`no_clip_mode` 调试用
