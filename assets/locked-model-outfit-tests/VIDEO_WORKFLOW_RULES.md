# Video generation workflow — mandatory order

## 2026-09-08 现行身份、提示词与验收标准

本节替代下文冲突的历史默认值。用户当前明确指令优先，其次为本项目人物锚点与制作标准、适用 skill；知识卡仅辅助，冲突建议丢弃。单套生活展示不强加变装、四套、户外、步行、音乐或15秒。参数沿用当前任务已确定值，不能因模型切换丢失。

### 0. 2026-09-08 运动穿搭失败复盘与真人感强制门槛

本节源于 2026-09-08 四条运动穿搭视频失败复盘，属于现行强制生产与验收规则。四条结果虽然基本保留身份与服装结构，但活人感、动作连续性和镜头表现不合格，状态不得记为“验收通过”，也不建议直接发布。仅凭稀疏抽帧确认脸和服装属于验收错误。

#### 已确认根因

- 关键帧过度精修，皮肤、发丝、身材和豪华背景过于完美，首帧已呈商业渲染或虚拟模特感。
- 扶墙、摸窗框、原地整理衣摆等动作缺少生活动机，像执行指令而非被亲近者随手拍到。
- 提示词堆叠“不要动、保持固定、只能移动几厘米”等冻结式限制，导致身体冻结，仅剩头和手机械运动。
- 用一个微动作填充 10 秒，模型以自动推近、僵硬微笑和姿态漂移补足时间。
- 首帧处于迈步或转身状态，却同时要求绝对固定镜头和脚底不动，动作与摄影约束冲突。
- 单张静态图只能锁定外观，不能提供真实重心转移、呼吸、肩胯联动和动作节奏。
- 仅以 1–2 fps 稀疏抽帧验收，无法识别木偶感、拖沓节奏和连续动作异常。

#### 强制生产规则

1. 关键帧除身份和服装外，必须通过“真人抓拍感”门槛：保留毛孔、轻微肤色变化、自然唇纹、碎发、真实衣褶、接触阴影及轻微非完美构图。精修海报感、瓷娃娃皮肤、假发感、过度对称和豪华样板间渲染感一律退回。
2. 单张关键帧图生视频默认采用单镜头 5–6 秒，不得用一个轻微动作硬撑 10 秒。需要 10 秒以上时，拆成两个有明确行为动机的短镜头，或使用可靠的首尾帧／动作参考流程。
3. 动作必须有生活动机。优先使用：拿起或放下水杯、放下手机、坐到沙发或床沿、整理耳机、翻一页书、伸展后自然放松、听到画外人后转头回应、自然笑后移开视线。默认禁用扶墙、摸窗框、长时间捏衣摆、持续摆拍和无原因慢转身。
4. 每段只保留一个完整主动作，同时写清真实动力链：目光先到目标 → 头部跟随 → 肩胸轻微联动 → 手臂完成动作 → 身体自然回落。不得只让头部或手部孤立运动。
5. 提示词以正向表演描述为主，避免堆叠冻结式负面约束；只保留身份、服装、肢体、额外人物和明显背景错误等必要硬限制。
6. 摄影机逻辑必须与人物动作兼容：静坐可近距离固定；人物移动时允许轻微自然跟随。不得同时要求明显步行／转身与绝对固定镜头。未经用户要求，不得自动大幅推近、裁掉头部或从全身变成胸腰特写。
7. 持续走路必须有真人动作参考、首尾关键帧或经验证的运动控制链路；只有单张静态关键帧时不默认持续走路。确需行走时只安排 1–2 个短步，并检查支撑脚、摆动脚、落地、重心移交和接触阴影。
8. 男友视角的核心是自然观察和短暂回应，而非持续盯镜头、刻意扭胯或摆姿。视线应在环境、手中物品与画外伴侣之间自然切换。
9. 生图阶段不能只追求固定脸和漂亮身材；“同一个人但像 AI 模特”仍判失败。背景优先选择真实、有轻微生活痕迹和自然光变化的空间。
10. 若视频模型仅支持单首帧且不能可靠控制长动作，应降低单条动作复杂度与时长，不得依赖更长、更复杂的文字假装解决运动物理问题。

#### 强制验收门槛

1. 身份验收、服装验收、活人感验收、动作物理验收和镜头验收必须分别记录，五项全部通过才可交付。
2. 必须以正常速度和 0.5 倍速连续播放成片；稀疏抽帧只作辅助，不能单独证明通过。
3. 连续检查呼吸、眨眼、视线先后关系、头颈肩联动、肩胯联动、脚底受力、重心转移、手与物体接触、衣料次级运动和镜头运动。
4. 出现任一情况即不通过：人物像木偶或虚拟模特、动作无动机、头或手孤立机械运动、动作被过度拉长、明显自动推近、头部被长时间裁切、脚底滑动、表情突然切换、身体重心不成立。
5. “生成成功”只代表任务完成；“脸和衣服没变”也不足以通过。不得把技术成功或稀疏抽帧正常再次误判为成片合格。

### 1. 参考素材分离

- 唯一固定女性身份原图：`/Users/apple/Documents/ChatGPT/群控/assets/model-templates/locked-model-frontal-v2.png`。
- 每次生图和每次修图都实际附上该原图，标为身份参考1；另附编辑目标。仅写“同一张脸”或文件路径不算使用参考。
- 锁定五官比例、眼形眼距、鼻唇、脸型下颌、年龄感、肤色与身材骨骼比例。妆容、发型变化仅按已授权范围，不得重设计人物。
- 背景含人物时，先生成并检查无人背景再参与角色合成，不能把含其他人物的背景直接混作身份参考。商品图含人时只提取衣服，移除人物头脸、界面和无关素材。图中白底不能误读成白布。
- 必须保留款式、领口、肩带、袖型、长度、贴身程度、抽褶、蕾丝和上下装关系；不确定的核心结构先核对原图。没有合格的无人背景或服装参考时，不假装处理已完成。

### 2. 关键帧验收门槛

- 先生成关键帧再生成视频。把结果与原始模特并排核对脸型、五官、肤色、发际线及身体比例，检查服装结构、手脚、接触阴影和环境光。
- 不使用脸被遮挡、过小或角度过偏的画面来声称身份通过；需要时补可核验视角。不能把含其他人物特征的结果作为新的母版。
- 原始模特锚点始终传入后续修图；修衣服、去包也不能只用已漂移的图继续修改。
- 状态必须为“待验收 / 通过 / 不通过”。只有通过或用户明确指定接受的关键帧才能进入视频；用户指定使用时记录“用户选定”，不得冒称客观无缺陷。

### 3. 可执行的视频提示词

- 保存完整版，不以几句泛泛描述代替：参考图角色映射、身份和款式不变量、时长/画幅/分辨率、镜头位置、分时段动作、视线与表情、支撑关系、物件轨迹、衣料反应、声音、负面限制。
- 每段只安排一个主动作，写出起点、接触、终点和停顿；避免同段叠加走路、转身、接物、运镜。
- 坐姿示例：臀部持续接触同一坐垫位置、双脚落点稳定；右手抬杯到嘴边再落回膝旁，左手维持支撑，视线随杯子移动后短暂看镜头旁。允许自然呼吸与微调，不要求全身僵硬冻结。
- 步行仅在剧情需要时使用短步；明确支撑脚不滑动、摆动脚抬起再落地、重心移交与接触阴影。出现漂移反馈后优先有支撑的坐姿动作，不默认连续走路。
- 男友视角以自然观察和短暂互动为主，不持续盯镜头，不夸张扭胯或刻意摆姿。真实皮肤、发丝和布料随同一环境光变化。
- 最终提示词记录每项来源 `[identity]`、`[user]`、`[skill]`、`[card:文件]`；只标实际读到的来源。提交文本可用自然语言，来源映射保留在本地。

### 4. 提交核验与防重复

- 图片引擎沿用 ChatGPT ImageGen；视频引擎按当前已约定执行（本轮 MiniMax H3）。不能因接力任务网络失败擅自换供应商或降低分辨率。
- 视频只提交该条验收通过/用户选定的关键帧。核对实际上传缩略图或API实际携带的图片数据/上传ID，不能只传本地路径文本。清除旧服装、旧脸和无关附件。
- 逐条绑定关键帧路径及哈希、完整提示词、实际模型和参数、任务ID、提交响应。状态必须区分未提交、排队、运行、生成成功待验收、验收通过、失败。
- 超时或返回不明确时先查询既有任务和账本，不能盲目重复提交扣费。明确失败才判断是否可修复；权限、额度或审核拦截如实报告，不宣称已提交或已完成。

### 5. 视频验收与交付

- 检查实际文件时长、编码和分辨率；1080p须核对视频像素，不能把提示词中的1080p视为事实，后期放大须明示。
- 检查开头、中段、结尾及转头/抬手/物件接触动作前后帧；评估脸型五官、发际线肤色、身材、款式连续性、额外人物、手指、物件形变、脚底滑动、坐垫支撑、背景漂移。
- 关键动作需连续回放或密集抽帧，稀疏抽帧不能证明没有运动漂移。无法检查的项目标“未验证”。明显身份漂移或肢体错误不能作为合格成片交付。
- 不合格结果保留为失败样本；只在原授权范围修复，不无限自动重试。用户要求本次不重做时记录缺陷，下次调整动作。
- 保存参考图清单、完整提示词、任务ID、成片路径和验收结果至当次 `assets/daily-outfits/YYYY-MM-DD/`。按已授权目的地交付；发布抖音必须有相应发布授权。

执行检查单：原始身份图实际附加 → 无人背景/服装单独参考 → 关键帧验收 → 精确动作脚本与冲突检查 → 实际引用核验 → 返回任务ID → 文件与人物/动作验收 → 成片交付。

## Constraint hierarchy and pre-generation conflict gate

This workflow is subordinate to the installed **`female-outfit-director` transformation skill**, which is the highest-priority and sole source of truth for multi-look transformation work.

1. **Transformation skill — highest priority / source of truth.** It governs identity invariants (face shape, facial-feature proportions, body proportions), adult identity continuity, controlled-variable boundaries, outfit-transition continuity, action and physical continuity, first/last-frame requirements, and image/video generation requirements.
2. **Shot-analysis knowledge cards — auxiliary retrieval layer only.** They may recommend a content goal, pacing, hook, CTA, visual anchor, styling narrative, or framing pattern.
3. **Current task instructions — allowed only when compatible.** A user-provided shot, outfit, duration, or requested template may specialise the skill but may not weaken its identity, continuity, physical-realism, or generation constraints.

### Required conflict check

Before generating any still or video prompt:

- Extract every applicable transformation-skill constraint first.
- Retrieve only the relevant knowledge-card recommendations for the selected content goal.
- Compare every card recommendation against the skill and discard the card recommendation immediately if it conflicts. Never modify, dilute, or override the skill to preserve a card-derived idea.
- Mark each final prompt constraint with its origin: `[skill]`, `[card:<card-id>]`, or `[user-compatible]`.
- Include a short **Conflict check: passed** record in the generation handoff. If a requested card idea conflicts with the skill, state that it was discarded and why before generating.

The skill’s variable boundaries are binding. Knowledge cards may add variation in compatible areas (such as content structure, title placement, CTA, accessory narrative, pacing, or a simple action), but never change the locked face shape, facial-feature proportions, body proportions, identity continuity, or action/transition physics.

For every Grok Imagine fashion-video generation, follow this order without exception:

1. Generate the selected, video-compatible outfit keyframes using the **front-facing locked identity image** during the image stage. Each accepted keyframe must already visibly contain the same locked model.
2. Upload **only** the selected outfit keyframes as video-reference attachments. Do not upload a separate facial identity image again unless the user explicitly asks for an identity re-lock.
3. Verify that the workflow explicitly confirms receipt/upload of the exact selected keyframes. Local filesystem paths in text are **not** proof of upload.
4. Only after confirmation, send the English-only video prompt, explicitly mapping each attachment to its look/scene role and requiring the same face already embedded in the frames.
5. Before calling a generation submitted, verify the workflow reports that it is using the uploaded keyframes and that no prior outfits or unrelated references remain attached.

Never submit a video prompt before the reference attachments are confirmed.

### Fixed image-stage engine

The default and required keyframe engine is **ChatGPT ImageGen**. Grok Imagine is the video-stage engine only. If ChatGPT ImageGen fails, pauses, or returns an authorization error, stop the workflow and report the exact failure. Do **not** silently substitute Grok, another image model, an old keyframe, or a previously generated asset. A different keyframe engine may be used only after the user explicitly approves that specific substitution.

## Default autonomous fashion-video runbook

When the user supplies new outfit references or says “use the default workflow”, execute the following without needing step-by-step direction:

1. **Identity lock at image stage** — use `assets/model-templates/locked-model-frontal-v2.png` as the sole facial identity anchor while making keyframes. Do not use a side-view image to lock the face. Once the final keyframes pass review, they become the identity-carrying references for the video stage.
2. **Look extraction** — identify the exact garments; only complete genuinely missing lower garments/shoes with a styling choice that suits the supplied top.
3. **Video-compatible keyframes** — make one 9:16 keyframe per look. Every image must have the same adult East Asian model, full body, both feet visible, a clear walking lane, an eye-level phone camera, and non-extreme pose topology. Use contemporary outdoor settings and purposeful accessories.
4. **Realism quality gate** — reject polished/CGI-looking drafts. Require real smartphone outdoor texture: natural skin and flyaway hair, cloth wrinkles, subtle scene imperfections, natural light and modest auto-exposure/white-balance variation.
5. **Reference-first transfer** — upload only the final keyframes to the target generation page/cloud computer. Confirm the exact expected number of attachment thumbnails is present and that there are no older outfit/identity images before any prompt is submitted.
6. **English-only video prompt** — map every keyframe attachment explicitly to its look/scene role; state that all frames already carry the locked identity, and that scene and accessory changes occur only during an action-based visual cover.
7. **Generation gate** — only generate after the target confirms it is using the uploaded images. Use 9:16, a single stable identity, continuous body movement, action-caused transitions, no text/watermark, and the current real-phone-texture constraints.
8. **Completion check** — report duration, aspect ratio, reference use, and visible defects. Do not download or publish unless the user asks.

Default delivery is a 15-second 9:16, four-look outdoor modern-fashion transformation with English prompt, 124–128 BPM instrumental/no vocals, and no automatic download or posting.

## Default visual tone — natural, non-greasy creator footage

This is the default unless the user explicitly asks for editorial glamour or a stylized concept.

- **Performance:** restrained and observant, like a stylish woman being casually filmed by a friend. Use natural walking, adjusting a hem, holding a bag, putting on/removing sunglasses, or a brief glance to camera. Avoid pouting, deliberate eyebrow poses, slow seductive hair flips, hip-sway posing, and extended runway-style holds.
- **Face and skin:** understated makeup; retain pores, small tonal variation, flyaway hair, subtle asymmetry, and ordinary micro-expressions. Never use porcelain/plastic skin or a virtual-avatar look.
- **Camera and light:** real iPhone creator footage at eye level, mostly stable but with slight hand-held micro-jitter, modest compression, natural daylight and environmental bounce. Allow subtle auto-exposure and white-balance shifts; avoid beauty-studio softness and hyper-clean commercial lighting.
- **Background:** use plausible, imperfect phone-shot locations rather than a flawless set: ordinary pavement wear, utility hardware, uneven planting, imperfect wall texture, occasional distant everyday context, and non-perfect framing are desirable. The background should feel lived-in and captured on location, not rendered as a luxury fashion campaign.
- **Scene continuity:** for multi-look transformation videos, default to one fixed real-world location. Keep camera position, focal length, background geometry, ambient light, and core props unchanged across every look. Let the model solve wardrobe and one simple action—not wardrobe, location, and camera movement at the same time. Change locations only when the user explicitly requests it.
- **Motion:** real-time speed only. Transitions must be action-caused (hand/palm, bag, sunglasses, turn, hair sweep) and coincide with music accents. No gratuitous slow motion, sensual body emphasis, or unexplained dramatic effects.
- **Accessories:** purposeful and physically plausible; an accessory may only appear/change during a complete visual cover or a clearly motivated transition.
- **Sound:** upbeat, clean 124–128 BPM instrumental with no vocals; rhythmic but not flirtatious, sultry, or overly “internet influencer” in tone.
- **Hard negatives:** no greasy influencer posing, no glamour-beauty filter, no exaggerated flirting, no glossy CGI, no plastic skin, no fashion-runway caricature, no slow-motion seduction.

## Mandatory visual-director and photographic realism review

Every image and video frame is reviewed through three simultaneous roles: **fashion visual director**, **real-portrait photographer**, and **image-quality reviewer**. A visually perfect but implausible AI model is a failed output.

### Human realism invariants

- Retain slight left/right facial asymmetry, visible pores, fine vellus hair, natural lip texture, under-eye texture, scattered flyaway strands, and skin texture appropriate to the model's adult age.
- Poses must obey believable centre of gravity, joint loading, muscle tension, and natural finger curvature. No floating body, rigid mannequin limbs, broken joints, or unnaturally splayed fingers.
- Clothing must respond to action with plausible tension, compression, drape, and wrinkles. Feet must make real ground contact with contact shadows.
- Skin, hair, clothing, and background must share one coherent environmental light direction, colour temperature, shadow softness, and exposure.
- Use restrained camera noise, natural depth of field, and slight exposure variation. Avoid synthetic over-sharpening.

### Automatic rejection list

Reject and regenerate any draft with porcelain-doll skin, perfectly symmetrical features, glassy eyes, plastic-looking clothing, wig-like hair texture, floating anatomy, inconsistent light, impossible garment folds, missing contact shadows, or excessive sharpening.

## Shot-analysis knowledge base — content structures and generation rules

Use visual shot analysis (not BGM ASR) to choose **one** primary content goal before writing a storyboard or video prompt. Do not combine the structures below in a single short-form video unless the user explicitly asks.

### Mandatory persistent shot-analysis cards

Every completed source-video analysis must create and persist an **independent knowledge card**; sending a summary in chat alone does not satisfy this requirement. Store one card per original video in `assets/shot-analysis-cards/videos/`, using a stable, searchable filename such as `YYYY-MM-DD--creator--short-title.md`.

Each individual-video card must include:

1. **Source metadata** — source URL, creator/author and title when available, local source filename when used, duration, frame size when known, analysis date, and tags.
2. **Content positioning and structure card** — intended audience, growth objective, beat-by-beat timing, and content-template classification.
3. **Shot and visual-template card** — scene, framing, camera behaviour, colour, styling anchors, cut rhythm, on-screen layout, and any usable visual reference frames.
4. **Growth-mechanism / hook / CTA card** — why the opening holds attention, where the interaction/save/conversion mechanism occurs, CTA wording/timing, and weaknesses.
5. **Reusable shooting and optimisation card** — elements that can be reproduced in our locked-model workflow, concrete improvement instructions, and anti-patterns to avoid.

Create separate **general-experience cards** in `assets/shot-analysis-cards/general/` for insights validated across more than one source. General cards must link back to the relevant individual-video cards and must never overwrite or replace them.

### 1. Fast-save capsule wardrobe collection

**Purpose:** rapid inspiration / saves.  
**Reference pattern:** a fixed full-body frame, a unified low-saturation palette, a series title and large look number; 6–9 looks flash in roughly 0.5–0.7 seconds each.

- Open in the first 0.5 seconds with an explicit benefit and count, for example: “9 Early-Autumn Outfit Ideas”.
- Keep one location, one camera position, one full-body framing, and one typography/numbering system.
- Vary clothing silhouette and colour while preserving all other visual anchors.
- Finish with a readable 0.8-second save prompt; numbers must be large enough to read on a phone.
- Use this template for efficient capsule-wardrobe inspiration, not for detailed single-product persuasion.

### 2. Interactive vote / candidate-wall transformation

**Purpose:** comments and participation.  
**Reference pattern:** the real model is in the main frame while several small, consistent-outlined candidate outfit stickers preview the choices; the following beats reveal those outfits one by one.

- Start with a clear choice and audience benefit, e.g. “6 Date Looks — Which One Flatters a Curvy Frame?”.
- The candidate wall must create a real choice, then the video must fulfil it with the same looks.
- Give each look a visible number and one short suitability cue when text is used.
- Use 1.5–2 seconds per look and end with a direct comment request such as “Comment 1–6”.
- Protect the model’s face and body: text and stickers may not crowd the first screen or obscure the product.

### 3. Mood-led multi-look editorial

**Purpose:** aesthetic appeal / product seeding.  
**Reference pattern:** a fixed outdoor full-body scene, a repeated personal anchor (tote, sunglasses, or similar), and a low-saturation base palette with controlled colour variation.

- Limit to 6–8 looks; organise them into simple real-life chapters such as commute, weekend, and travel.
- Add the audience benefit during the first 3 seconds, rather than using only an emotional line.
- Keep the same stance, framing, accessory anchor, location, and camera look so clothing changes are legible.
- End with a concrete save action, for example “Save this colour formula”.

### 4. Dynamic lookbook plus compact knowledge card

**Purpose:** saves, conversion, and reusable styling knowledge.  
**Reference pattern:** each of four looks follows a repeated unit: full-body motion (front plus turn/side/back) followed by a simple information card.

- Use LOOK01–04 or an equivalent clear numbering system.
- The first screen states a user benefit, e.g. “4 Smart Casual Office Outfit Templates”, never a production-centric claim such as “AI video test”.
- Every card contains only three readable lines: **occasion**, **hero piece**, and **proportion/styling logic**. Move any longer explanation to caption or comments.
- Treat the dynamic lookbook and information card as a cohesive system: consistent title position, palette, type scale, background, and timing.

### Cross-template non-negotiables

- One short video has one principal growth objective: **save**, **comment**, **mood-led seeding**, or **styling knowledge**.
- Preserve fixed scene/camera, a full-body view, and exactly one durable visual anchor (large look title/number, stickers, tote, sunglasses, etc.). Allow the clothing and colour palette to carry the variation.
- In any transformation cut, assign exactly one simple motion instruction per look: take one grounded step, turn, lift a hand, adjust an accessory, or settle a hem. Avoid piling multiple motions into a single beat.
- Put the benefit in the first three seconds. Keep CTA to 1.5–2 seconds except fast-save collections, which reserve a readable 0.8-second end card.
- For an outfit/product selling point, reserve one 0.3–0.5-second detail beat every two looks: collar, waistline, pleats, hem, fabric drape, shoe, or bag. Never cover the face or product with text.
- Analyse fashion references visually frame-by-frame. Do not derive the video structure from automatic BGM lyric transcription.
