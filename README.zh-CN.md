# Editorial Diagrams

[English](README.md) | 简体中文

一个 Agent Skill：用一句自然语言描述，生成精确、可编辑、带流向动画的技术图，风格接近经过编辑排版的工程技术文章里的配图。

**在线案例：**[Codex CLI 运行架构](https://codex-architecture-site.vercel.app/)，由本 skill 根据 `openai/codex` 源码生成。

[![用 Editorial Diagrams 绘制的 Codex CLI 架构图](docs/images/06-codex-cli-zh-CN.png)](https://codex-architecture-site.vercel.app/)

## 名字里的 “Editorial” 是什么意思

“Editorial” 指的是出版物和工程博客中、随文章一起出现的“文章插图”：有图号、标题、一段说明、图例和来源注释，中间是一张克制的黑白技术图。这个 skill 生成的就是这种插图，而不是白板草图或自动布局的关系图：

- 白底加细点阵网格，1px 深色边框，4px 卡片圆角；
- 卡片和分组对齐，连线只走水平和垂直方向，带箭头；
- 小型动画标记表示方向：方块表示请求，圆点表示返回，菱形表示异步变化；
- 带文字的播放 / 暂停按钮、图例，以及记录前提和来源的注释。

## 安装

使用 [skills.sh](https://skills.sh)：

```bash
npx skills add wyh0626/editorial-diagrams
```

全局安装到指定的 Agent：

```bash
npx skills add wyh0626/editorial-diagrams -g -a claude-code
```

```bash
npx skills add wyh0626/editorial-diagrams -g -a codex
```

手动安装：把 [`skills/editorial-diagrams`](skills/editorial-diagrams) 复制到 Agent 的 skills 目录，例如 `~/.claude/skills/editorial-diagrams`。

## 使用

用任意语言向 Agent 提需求：

```text
/editorial-diagrams 画一张这个仓库的架构图
```

```text
用 editorial-diagrams 画出请求经过 API 网关的流程
```

Agent 会读代码或描述、规划布局、编写 JSON 配置、渲染，并在浏览器中检查结果。产出：

| 文件 | 用途 |
| --- | --- |
| `diagram.json` | 可编辑的源数据：节点、分组、连线和文字 |
| `diagram.html` | 自包含的交互页面（CSS 和 JS 全部内联，不发网络请求） |
| `diagram.png` | 可选预览图，宿主支持浏览器截图时生成 |

生成的页面会跟随对话语言，包括按钮文字和无障碍标签。

## 手动渲染

渲染器只需要 Python 3.8+，没有其他依赖。

```bash
python3 skills/editorial-diagrams/scripts/render.py --data skills/editorial-diagrams/examples/01-api-gateway.json --output out/api-gateway.html
```

- `--instance <id>`：指定固定的根元素 ID。
- `--fragment`：输出可嵌入的片段，而不是完整页面。

写文件前，渲染器会校验几何结构：是否超出画布、ID 是否重复、节点是否重叠、连线是否只有水平 / 垂直线段、端点是否落在节点边框上、连线是否穿过无关节点。它无法测量文字宽度，所以还需要在浏览器里检查：

| 参数 | 作用 |
| --- | --- |
| `?time=2.4` | 把动画冻结在 2.4 秒，便于稳定截图 |
| `?scroll=500` | 横向滚动画布 |
| `?check=1` | 给溢出卡片的文字加红框，并在 `data-overflow` 中给出数量 |

配置格式见 [`references/graph-format.md`](skills/editorial-diagrams/references/graph-format.md)。

## 示例

| | |
| --- | --- |
| [![API 网关](docs/images/01-api-gateway.png)](skills/editorial-diagrams/examples/01-api-gateway.json) | [![订单事件](docs/images/02-order-events.png)](skills/editorial-diagrams/examples/02-order-events.json) |
| API 网关与业务服务 | 先提交事务，再发布事件 |
| [![RAG](docs/images/03-rag.png)](skills/editorial-diagrams/examples/03-rag.json) | [![跨区域复制](docs/images/04-regional-replication.png)](skills/editorial-diagrams/examples/04-regional-replication.json) |
| 查询与知识入库分离的 RAG | 主库写入，本地只读查询 |
| [![HTTP/3](docs/images/05-http3.png)](skills/editorial-diagrams/examples/05-http3.json) | [![Codex CLI](docs/images/06-codex-cli-zh-CN.png)](skills/editorial-diagrams/examples/06-codex-cli-zh-CN.json) |
| 一条 QUIC 连接上的多个 HTTP/3 流 | Codex CLI 运行架构（简体中文） |

示例只是拓扑上的起点，不是需要套用的模板。

## 仓库结构

```text
skills/editorial-diagrams/
├── SKILL.md                  # Agent 遵循的说明
├── agents/openai.yaml        # Codex 的展示元数据
├── assets/                   # 样式、图标几何、播放脚本
├── examples/                 # 示例 JSON 配置
├── references/graph-format.md
└── scripts/render.py         # 仅依赖标准库的渲染与校验脚本
docs/images/                  # README 预览图
```

## 说明

- 动画只表示方向，不代表延迟、吞吐量或数据包数量。
- 使用系统字体和原创的简单几何图标，不包含任何从网站提取的代码、专有字体或品牌素材。
- 这是独立的社区项目，与 OpenAI 及任何启发了视觉风格的出版物没有关联，也未获其背书。Codex 示例描述的是公开的 `openai/codex` 仓库。

## 许可证

[MIT](LICENSE)
