---
workflow: general-video
flow: automation
storyboard: no
message: "男友镜头里的三套宽松T恤日常"
destination: douyin
aspect: 1080x1920
language: zh
length: 15s
angle: candid-lifestyle
---

## Intent

用户要求今天三套只做一个视频，可以分批生成再用HyperFrames串联。延续男友视角，不做变装；露腿，内搭短裤由上衣盖住。沿用固定女性模特与1080p要求。继续此前自主编排的工作方式，无需重新做需求问卷。

## Assets

- ../../assets/daily-outfits/2026-09-08/look01-white-keyframe.png — 白T，椅上拿杯。
- ../../assets/daily-outfits/2026-09-08/look02-grey-keyframe.png — 浅灰T，床沿整袖。
- ../../assets/daily-outfits/2026-09-08/look03-jeep-keyframe.png — 米灰T，床沿读书。
- ../../assets/daily-outfits/2026-09-08/look01-task.json — 第一段任务与完整提示词。
- ../../assets/daily-outfits/2026-09-08/look02-task.json — 第二段任务与完整提示词。
- ../../assets/daily-outfits/2026-09-08/look03-task.json — 第三段任务与完整提示词。

## Customizations

HyperFrames仅串联剪辑真实返回的视频源片，不以静图动画代替。自然硬切，不添加换装特效。

## Notes

制作补全：总长约15秒，每个10秒源片选择约5秒，无额外音乐、字幕、旁白。保持环境声。人物不连续盯镜头、不走路。原始身份图每次实际参与生图；视频实际引用对应关键帧。提交回执已取得，生成后才做视频质量验收。最终预览检查完成再按HyperFrames流程申请导出确认；不自动发布抖音。
