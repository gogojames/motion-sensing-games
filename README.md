# Motion-Sensing Games

体感游戏 — 使用普通摄像头和 MediaPipe Pose Landmarker 实现的两款手势/体感游戏。

## 游戏

### 🍉 切水果 (Fruit Slicing)

玩家站在摄像头前，用手部挥动切开飞来的水果。

- 手掌快速划过水果即可切开
- 炸弹会立即结束游戏
- 漏掉 3 个水果游戏结束
- 连击加分，金色西瓜稀有出现 +50 分

**操作**: 挥手切水果 / `Space` 开始 / `P` 暂停 / `Esc` 退出

### 🎵 节奏指挥家 (Rhythm Conductor)

玩家用全身动作指挥乐队，音乐随动作实时变化。

- 手臂速度控制节奏快慢
- 手臂张开幅度控制音量
- 按提示完成手势获得分数
- 连击解锁音乐层次（鼓→贝斯→旋律→和声）
- 能量满触发 Supernova 模式

**操作**: 全身动作 / `Space` 开始 / `P` 暂停 / `Esc` 退出

## 安装

### 要求

- Python 3.11 或 3.12
- 普通 USB 摄像头
- macOS 或 Windows

### 安装步骤

```bash
# 克隆仓库
git clone <repo-url>
cd motion-sensing-games

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

首次运行会自动下载 MediaPipe Pose Landmarker 模型（~5.5MB），之后完全离线运行。

### 命令行参数

```
python main.py [选项]

选项:
  --camera-id ID    摄像头设备 ID (默认: 0)
  --fullscreen      全屏模式
  --no-sound        禁用声音
```

## 技术栈

| 技术 | 用途 |
|------|------|
| MediaPipe Pose Landmarker | 姿态识别（33 个关键点，30Hz） |
| OpenCV | 摄像头视频流 |
| NumPy | 数学计算、程序化音频合成 |
| Pygame | 图形渲染（60fps）、音频播放 |

## 项目结构

```
motion-sensing-games/
├── main.py                 # 入口
├── common/                 # 公共模块
│   ├── config.py           # 配置管理
│   ├── camera.py           # 摄像头控制
│   ├── calibration.py      # 2秒姿态校准
│   ├── scores.py           # 分数持久化
│   ├── menu.py             # 主菜单
│   ├── model_downloader.py # 模型下载
│   └── sys_ui.py           # 系统原生对话框
├── pose/                   # 姿态识别
│   ├── detector.py         # MediaPipe 封装
│   ├── landmarks.py        # 关键点数学计算
│   └── thread.py           # 30Hz 后台检测线程
├── fruit_slicing/          # 切水果游戏
│   ├── entities.py         # 水果、炸弹、手刃
│   ├── spawner.py          # 波次生成
│   ├── collision.py        # 碰撞检测
│   ├── scoring.py          # 计分引擎
│   ├── audio.py            # 程序化音效
│   ├── renderer.py         # 图形渲染
│   └── game.py             # 游戏主循环
├── conductor/              # 节奏指挥家游戏
│   ├── targets.py          # 星符目标系统
│   ├── gesture.py          # 全身手势分类
│   ├── music.py            # 4层程序化音乐
│   ├── scoring.py          # 计分 + 能量系统
│   ├── renderer.py         # 星空 + 目标渲染
│   └── game.py             # 游戏主循环
├── tests/                  # 单元测试
│   ├── test_landmarks.py
│   ├── test_collision.py
│   ├── test_scoring.py
│   └── test_spawner.py
├── models/                 # 姿态模型 (gitignored)
├── data/                   # 用户数据 (gitignored)
└── requirements.txt
```

## 运行测试

```bash
pip install pytest
pytest tests/ -v
```

## 隐私

- 所有处理在本地完成，无联网请求（仅首次下载模型）
- 摄像头画面绝不写入磁盘或上传
- 所有图形和音效程序化生成，仓库中无任何媒体素材
