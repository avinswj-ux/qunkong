# 2026-09-08 晚间运动穿搭成片验收

## 执行基线

- 中央规则任务：`01a08135-2b48-7ae0-ba27-7359f6517610`
- 唯一人脸锚点：`assets/model-templates/locked-model-frontal-v2.png`
- 身材辅助参考：`assets/model-templates/locked-model-views-body-v3.png`
- 图片引擎：ChatGPT ImageGen
- 视频引擎：MiniMax H3，`minimax_h3_lightx2v_v5`
- 冲突检查：通过；商品图仅用于服装，视频每条仅上传对应的已验收关键帧。

## 生成任务

| Look | 关键帧 | 任务 ID | 原始返回 | 精确 1080×1920 交付版 |
|---|---|---|---|---|
| 01 | `look-01-gray-vest-black-biker-keyframe.png` | `56a18a54-a7ce-459c-b1a5-b74968619058` | 1056×1920 / 10.125s | `/Users/apple/Desktop/抖音成片/2026-09-08/look-01-gray-vest-black-biker-10s-1080p-exact-1080x1920.mp4` |
| 02 | `look-02-gray-flare-flipflops-keyframe.png` | `6d8826b3-6049-49a5-9c3e-7677b0e4c003` | 1056×1920 / 10.125s | `/Users/apple/Desktop/抖音成片/2026-09-08/look-02-gray-flare-flipflops-10s-1080p-exact-1080x1920.mp4` |
| 03 | `look-03-brown-leggings-oatmeal-top-keyframe.png` | `3fa7c212-d4ec-451b-94ae-bc71e14244a4` | 1056×1920 / 10.125s | `/Users/apple/Desktop/抖音成片/2026-09-08/look-03-brown-leggings-oatmeal-top-10s-1080p-exact-1080x1920.mp4` |
| 04 | `look-04-gray-openback-black-biker-keyframe.png` | `f29cecff-268f-469b-bd91-7be27b0a1953` | 1056×1920 / 10.125s | `/Users/apple/Desktop/抖音成片/2026-09-08/look-04-gray-openback-black-biker-10s-1080p-exact-1080x1920.mp4` |

## 抽帧验收

- 身份：四条开头、中段、结尾保持同一固定女性模特；未见明显换脸或沿用商品模特。
- 服装：Look 01 背心结构线与黑色骑行短裤保持；Look 02 灰色喇叭裤与黑色人字拖保持；Look 03 深棕紧身长裤保持；Look 04 X 形肩带、后腰扭结与黑色骑行短裤保持。
- 人体：抽帧未见第二人物、明显手脚增生或断裂；脚底保持可见接触关系。
- 场景：酒店走廊整体连续，无突然换景。
- 已知瑕疵：模型生成期间存在轻微到明显的自动推近/构图变化，Look 01 最明显；这不是身份漂移，但没有完全满足“近乎固定机位”。未发现必须阻止交付的服装或身份错误。
- 分辨率说明：MiniMax H3 原始文件实际为 1056×1920；交付版经 Lanczos 放大并轻裁切为精确 1080×1920，保留原始文件以供核对。

## 结论

状态：通过交付（带已知轻微机位推近说明）。
