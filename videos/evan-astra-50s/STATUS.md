# 当前状态

2026-09-08 21:08:41 北京时间再次按用户要求以 `seedance-test2` 提交 v18。服务端回执同时明确 model=`seedance-test2`、group=`seedance-test2 (distributor)`，HTTP 503 `model_not_found`。请求编号 `202609081308419234231408268d9d6cIsSFsaJ`，回执 `jobs/fictional-02-v18-response.json`。本次不能归因于仍在 test1 分组，未取得任务 ID。

## 最新用户指令与实测（2026-09-08 16:54）

用户明确要求模型名必须为 `seedance-test2`，不得再调用旧 Seedance 2.5 名称。脚本已改回该模型。v16 旧模型请求的本地进程已终止，终止前未收到回执；上游是否受理未知，本地终止不等于远端取消。v17 使用 `seedance-test2` 和第一幕视频参考实际提交，返回 HTTP 503 `model_not_found`：`No available channel for model seedance-test2 under group seedance-test2 (distributor)`。当前令牌分组已确认为 T2，但模型通道仍不可用；本次没有创建可追踪任务。下文分组/模型名推断被本段明确指令与最新证据覆盖。

## T2 分组与模型名更正

用户截图确认 `seedance-test2` 是令牌分组，不是模型名。此前 v14/v15 将其作为模型名提交，不能据此判断 T2 线路是否可用。脚本默认模型已恢复为 `/v1/models` 实际列出的 `AP Seedance-2.5 标准版`；v16 使用第一幕视频参考提交，等待回执。分组由服务端令牌配置决定，截图里的编辑选中值本身不证明已保存。

## 2026-09-08 T2 线路测试

2026-09-08 16:45（北京时间）按用户要求再次提交 v15，模型仍为 `seedance-test2`，继续使用第一幕视频参考；仍返回 HTTP 503 `model_not_found`，明确指出 `seedance-test1 (distributor)` 分组没有该模型可用通道。未取得任务 ID；回执保存在 `jobs/fictional-02-v15-response.json`。

用户指定完整模型名 `seedance-test2`。第二幕脚本默认模型已切换为该值，v14 沿用第一幕虚构人物视频参考提交 `/v1/videos`。返回 HTTP 503 `model_not_found`：`No available channel for model seedance-test2 under group seedance-test1 (distributor)`。当前密钥路由到 seedance-test1 分组，无法访问 seedance-test2 模型；未创建新任务。需平台给当前令牌配置可访问 T2 模型的分组/通道，或使用已有 T2 令牌。

## 2026-09-08 第二幕恢复实测

用户告知 DonaAPI 已修复 202，并确认继续以第一幕虚构人物锁定身份。此次沿用本地 `fictional-01.mp4` 及其清晰帧；v10–v12 的 `/v1/videos` 请求均返回 HTTP 400、上游 `InvalidParameter`，明确指向 `content`。补齐 text 项及改为 image_url reference_image 后仍未通过。v13 使用单图 `/v1/video/generations` 返回 HTTP 503 `model_not_found`，指出 test1 (distributor) 分组没有该模型可用通道。本次未返回隐私拦截，也未取得可查询的新任务或第二幕视频。第一幕历史 content 地址 HEAD 返回 410，本地母版保留完整。

当前阻塞应按上述最新参数/通道错误排查；不能再仅依据旧 202 回执判断当前网关状态，也不能将本次失败归因真人隐私。恢复需该通道可用的参考素材请求示例及有效模型路由。

2026-09-07：未产出最终真人成片。已完成4张身份参考关键帧、六幕50秒分镜和HyperFrames关键帧预演工程。

## 可查看成果

- Studio：http://localhost:4574/#project/evan-astra-50s ，已确认HTTP200。
- `npm run check -- --json --at 4,11,18,26,35,44 --snapshots`通过：lint/runtime/layout/contrast无错误，32项文字对比度检查通过。
- 已目视检查六幕中点及48.5秒结尾截图。预演用静态关键帧、字幕和状态进度，无配音，不是最终真人视频。
- 使用HyperFrames 0.8.30，版本检查显示已为当前版本。
- 分镜参考手册用于固定六幕的状态时序和进度条；素材不额外套用颜色滤镜，保留暖光及球场原有质感。

## Seedance 2.5接口验收

- GET /v1/models成功，存在AP Seedance-2.5 标准版。
- 原始JSON顶层first_frame被忽略，生成8.064秒带音轨视频，但人物及房间均错误，已拒收。
- 使用content数组、image_url及role:first_frame后，说明图片真正进入上游。
- 单独ratio字段触发invalid_ratio；使用size:1280x720后通过该校验。
- 最终明确返回400：InputImageSensitiveContentDetected.PrivacyInformation，content[1]真人图片需要平台侧完成授权。
- 改用原创虚构人物后，纯文本首段 `task_ARjcmWicDXzFKEuKaLB0p0xoTMP2Jfcc` 已完成，下载为 `assets/video/fictional-01.mp4`，8.064秒，1278×720，含音轨；四点接触表检查通过，作为人物母版。
- 使用该母版视频作为 `video_url` 参考生成磨豆段时，Dona 返回 HTTP 202 并把排队信息嵌在 `fail_to_fetch_task` 字段；返回的临时ID随后查询为 `task_not_exist`，列表接口也出现短暂 `Invalid URL`，因此没有把它当作成功，也没有继续重复提交。
- 2026-09-07 修复本地 Dona 传输层：无参考请求改走 `/v1/video/generations`，单图请求使用 `image`、`duration`、`width`、`height`，多媒体请求保留 OpenAI `content` 兼容路径；轮询任务同时记录对应查询端点，并接受 `succeeded` / `completed` 状态。网关返回 `fail_to_fetch_task` 时不再把嵌套的 queued 回执当作可追踪任务。
- 该修复只修正本地请求与状态判断，不能绕过上游对写实人脸参考图的隐私拦截；当前 DonaAPI 仍未持久化 Seedance 任务，生成链路仍需平台侧修复后才能继续。
- 2026-09-07 第二段再次提交（沿用已完成的虚构 Evan 视频作为 video_url 参考）仍只得到 `fail_to_fetch_task` 包裹的 queued 回执；随后查询 `/v1/videos/{id}`、`/v1/video/generations/{id}` 均返回 `task_not_exist`，未下载或挂载第二段素材。
- 请求ID：021788771029694806bb4b5cb47af996838ad42b320db36dbe990。
- 不再重复提交，不更换脸、不绕过真人保护，不把关键帧预演当成Seedance成片。

## 下一步所需

请DonaAPI提供Seedance真人素材授权的操作流程及API参数（例如授权素材ID如何传入），或提供已完成该授权且支持本人形象图生视频的通道。用户已在本对话中明确授权使用Evan本人形象，但这不等同于上游平台已登记授权。

恢复时先解决授权，再运行jobs/generate.mjs；现有attempt文件防止重复提交，不应直接删除它来反复重试。使用新的版本化任务记录保留每次回执。
