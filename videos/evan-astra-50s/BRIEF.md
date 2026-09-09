---
workflow: general-video
flow: automation
storyboard: no
length: 50s
aspect: 16:9
language: zh-CN
message: Evan交代目标，Astra持续执行，Evan继续生活。
---

# 已确认制作要求
用户已授权生成关键帧、调用其DonaAPI Seedance 2.5接口，并由HyperFrames渲染成片。
全片第三人称观察视角，人物不看镜头。最新用户确认改为Seedance 2.5自行生成的原创虚构男主Evan，180cm、74kg，不再使用或模仿用户本人照片。旧照片衍生关键帧仅保留历史版本，不用于新生成请求或最终成片。
室内深灰衬衫与深裤；球场深灰运动T恤、黑短裤。保持脸、发型、肤色和体型。
六幕：研判请求、磨豆同时后台分析、报告与选款、搭配生成剪辑、手冲时安排每4小时发布、球场休息接收数据。
真实API数据尚未提供，UI演示内容必须标明示例。固定同一任务进度贯穿。

# 资产
assets/keyframes/01-study.png：室内对话母帧。
assets/keyframes/02-coffee.png：咖啡吧台母帧。
assets/keyframes/03-court.png：球场休息母帧。
原始身份参考：/Users/apple/Desktop/素材/Codex 图像 2026年9月7日 10_33_59.png。
关键帧使用内置imagegen生成。视频必须用AP Seedance-2.5 标准版，不替换成旧版。

# 执行状态
原首段task_y5kudqiy6jLEvMgfHH3b7qXDPKd3Lasm已完成但验收拒收：参考图字段未生效，人物及房间错误。
已按本机新版Dona专用接入修正为content数组中image_url与role:first_frame。size:1280x720进入真人图片校验后，被上游以InputImageSensitiveContentDetected.PrivacyInformation拒绝；需要平台侧完成真人授权，暂停后续收费生成，不重复提交。
新增assets/keyframes/04-grinder.png磨豆关键帧。六幕提示词保存在jobs/generate.mjs，密钥仅通过进程环境输入，项目不存储密钥。
