# Genshin Three.js Viewer

一个零构建步骤的模型查看器（支持 `.glb/.gltf/.pmx`），用于在浏览器里快速预览模型。

## 1) 启动本地服务

在本目录运行：

```bash
python3 -m http.server 8787
```

然后打开：`http://127.0.0.1:8787`

## 2) 放置模型

推荐把模型放在：

- `models/paimeng.glb`
- `models/paimeng_dance.glb`
- `models/paimeng.pmx`
- `models/Texture/*`（PMX 贴图）

当前页面默认尝试加载：

- `models/paimeng_dance.glb`

## 方案切换

页面内置了两种方案开关：

- `方案A: MMDLoader 直载 PMX` -> `models/paimeng.pmx`
- `方案B: Blender 转 GLB` -> `models/paimeng_dance.glb`

点击“切换方案并加载”即可立即切换测试。

## 3) 其他加载方式

页面支持：

- 输入路径后点击“按路径加载”
- 使用文件选择器加载 `.glb/.gltf`
- 拖拽模型文件到页面
- PMX 建议按路径加载（便于自动读取同目录贴图）

## 常见问题

- 目录权限问题：如果模型在你当前用户无读权限的目录，浏览器和本地服务都无法读取。
- `.gltf` 纹理丢失：确认 `.bin` 和贴图文件与 `.gltf` 的相对路径一致。
- `.pmx` 贴图丢失：确认 PMX 引用的纹理路径与 `Texture/` 目录一致，并保持原始目录结构。

## GitHub Pages 部署

本项目已兼容 `https://<user>.github.io/<repo>/` 子路径部署。

1. 推送仓库到 GitHub。
2. 在仓库 `Settings -> Pages` 中将 Source 设为 `GitHub Actions`。
3. 推送到 `main` 或 `master` 分支后，会自动触发部署。

部署完成后访问：

- `https://<user>.github.io/<repo>/`

## 导出脚本

仓库内置了 MMD 风格材质转 GLB 导出脚本：

- `scripts/export_mmd_textured_glb.py`

示例：

```bash
blender -b -P scripts/export_mmd_textured_glb.py -- \
  --input-blend /home/openclaw/paimeng/派蒙_跳舞动作.blend \
  --output-glb /home/openclaw/paimeng/paimeng_dance_textured.glb
```

## 本次已完成

- 已从 `~/paimeng/派蒙.blend` 导出 `~/paimeng/paimeng.glb`
- 已从 `~/paimeng/派蒙_跳舞动作.blend` 导出 `~/paimeng/paimeng_dance.glb`
- 已复制两份 GLB 到本项目的 `models/` 目录，开箱即用
