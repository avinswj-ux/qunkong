from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_BREAK

ROOT = Path('/Users/apple/Documents/ChatGPT/群控')
SRC = Path('/Users/apple/.codex/attachments/061147ec-1ef8-4bcf-bcc7-4d277cb6218c/pasted-text.txt')
ASSETS = ROOT / 'assets/M-001-imagine-redo'
DESKTOP = Path('/Users/apple/Desktop/M-001-Imagine-分镜与提示词-重制版')
IMG_DIR = DESKTOP / '01-分镜图片'
DOCX = DESKTOP / 'M-001-Imagine-完整分镜与提示词.docx'
MD = DESKTOP / 'M-001-Imagine-可复制提示词.md'

DESKTOP.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

source_text = SRC.read_text(encoding='utf-8')

supplement = r'''

---

# 补充规范｜原稿未明确但制作时必须锁定

## A. 文件与参考图顺序

- 所有步骤的第一张参考图固定为 `M-001-face-anchor-approved.png`，其余图片不得覆盖面部身份。
- 00 是动作与体型母版；03 是换装像素对齐母版；04–15 每次只能以上一张合格母版为编辑目标，不得重新文生图构图。
- 01、02、03 以及 15 必须分别作为三段视频的干净单帧来源；禁止使用分镜拼贴、旧视频或其他项目人物代替。
- 每次只提交当前步骤需要的参考图，避免模型把未指定服装、草帽、包或首饰带入下一帧。

## B. 图片统一技术参数

- 画布：9:16，建议原始尺寸 1024×1792 或更高；进入剪辑统一适配 720×1280。
- 色彩：sRGB；PNG；不叠加锐化、滤镜、文字、水印或滚轮。
- 固定机位：正面、视线高度、等效 50–70mm；不得改变透视、主体大小和地平线。
- 顶部 16%（约 205 px / 1280 高画布）为滚轮安全区，人物头发、手指和配件不得进入。
- 白底 RGB 应接近 248–255，避免灰墙、明显渐变、地面线或背景纹理。

## C. 逐帧身份与姿态验收

每张图进入剪辑前按以下顺序检查：

1. 双眼中心、鼻尖、嘴角、耳朵和发际线是否与母版重合。
2. 肩线、肘部、手腕、五指轮廓是否无位移；右手不得变成单指指天或插袋。
3. 髋部、膝盖、脚踝和鞋底是否与母版重合；不得双脚突然并拢、换重心或改变抬脚方向。
4. 服装以外的皮肤区域、身体轮廓、阴影和人物缩放是否完全不变。
5. 未指定配件必须删除；草帽只允许出现在 04、05、09、13，斜挎包只允许出现在 06、08、10。

建议把 04–15 以 4 fps 循环预览，并叠加 50% 透明度母版检查。任何一项漂移都只重做当前帧。

## D. 视频生成补充约束

- 三段视频统一：9:16、720p、6 秒、关闭生成音频、固定摄影机、单次单镜头。
- 生成后只截取指定区间，不强行使用完整 6 秒；禁止速度拉伸补时长。
- 开场视频最后一帧应选择人物已完成蓄力、但尚未跨出手机的画面。
- 跳出视频必须从 02 连续运动并落到 03；若无法首尾帧控制，宁可重新生成，不允许用旧素材拼接。
- 结尾视频第一帧必须与 15 像素级一致；脸或服装在首帧即变化则整段作废。

## E. 15 秒精确剪辑表（30 fps）

- 000–080（0.00–2.70s）：手机开场视频。
- 081–110（2.70–3.70s）：跳出手机视频。
- 111–383（3.70–12.80s）：12 张换装图；建议帧长依次为 22、14、14、14、23、14、14、14、23、14、14、31，总计 211 帧；剩余 62 帧用于停靠节奏、局部闪白和完整套装强调，可按音乐拍点微调，但总区间不得越界。
- 384–428（12.80–14.30s）：最终真人微动作。
- 429–449（14.30–15.00s）：结果锁定界面。

说明：完整套装 04/08/12/15 的可见停留应长于错配帧；切换只能硬切，不得使用溶解、液化或形变转场。

## F. 四条真实服装滚轮

- 轨道内容必须来自 04–15 的真实衣物裁切缩略图，不得用英文文字卡代替。
- 四轨从上到下建议为：上装 / 下装 / 鞋履 / 配件；每轨高度约 40–44 px，轨道总高度不得超过顶部 16% 安全区。
- 四轨速度不同并错峰停靠：建议 1.00×、1.14×、0.88×、1.26×；停靠前越位约半格，再用 4–6 帧回弹。
- 高速阶段只对轨道缩略图添加水平方向模糊，人物与背景不得模糊。
- 每次命中：2 帧暖黄描边（建议 #FFC84A）、1 帧白色小星芒、1 帧局部亮度闪烁，并在同一帧落 click 声。
- 滚轮不得遮挡头发、脸、右手或中文开场文字。

## G. 换装闪白与残影

- 切换前 1 帧：只在服装区域出现局部白闪，禁止整屏闪白。
- 新服装出现后的第 1 帧：保留上一套衣边 10%–15% 透明度残影；残影只覆盖衣物边缘，不覆盖脸、头发、皮肤或手。
- 第 2 帧恢复完全干净的新服装；人物身体、背景和镜头全程不动。

## H. 声音与结果界面

- 生成视频音频关闭；剪辑阶段独立添加音效。
- 每次服装命中使用短 click；完整套装可叠加极轻的高频 sparkle；结尾 14.30s 使用快门/锁定声。
- 结果界面推荐中文“穿搭锁定”，相机与刷新图标保持小型、线性、同一风格；不得大面积遮挡人物。
- 14.30–15.00s 只做轻微手机框放大回弹与结果文字出现，不再改变人物身份、服装或姿势。

## I. 最终导出与审片

- H.264 MP4，720×1280，30 fps，15.00 秒；音频 AAC 48 kHz。
- 先导出低码率审片版，逐帧检查 2.70s、3.70s、每个换装切点、12.80s、14.30s。
- 最终验收：同一张脸；人物无缩放/漂移；滚轮不遮脸；无旧视频混入；无整屏闪白；结尾首帧与 15 对齐；无额外 Logo、水印、二维码或错误文字。
'''

MD.write_text(source_text.rstrip() + supplement + '\n', encoding='utf-8')

image_names = [
    '00-标准动作母帧.png','01-手机开场.png','02-跳出手机.png','03-白底换装母帧.png',
    '04-A完整套装.png','05-错配01.png','06-错配02.png','07-错配03.png',
    '08-B完整套装.png','09-错配04.png','10-错配05.png','11-错配06.png',
    '12-C完整套装.png','13-错配07.png','14-错配08.png','15-D完整套装.png'
]
for name in image_names:
    src = ASSETS / name
    if src.exists():
        (IMG_DIR / name).write_bytes(src.read_bytes())

doc = Document()
sec = doc.sections[0]
sec.page_width = Inches(8.5)
sec.page_height = Inches(11)
sec.top_margin = Inches(0.72)
sec.bottom_margin = Inches(0.72)
sec.left_margin = Inches(0.78)
sec.right_margin = Inches(0.78)
sec.header_distance = Inches(0.35)
sec.footer_distance = Inches(0.35)

styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Arial Unicode MS'
normal._element.rPr.rFonts.set(qn('w:ascii'), 'Arial Unicode MS')
normal._element.rPr.rFonts.set(qn('w:hAnsi'), 'Arial Unicode MS')
normal._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Unicode MS')
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.2
for n, size, color, before, after in [
    ('Heading 1', 17, '1F4D78', 16, 8),
    ('Heading 2', 13, '2E74B5', 11, 5),
    ('Heading 3', 11.5, '1F4D78', 8, 4),
]:
    s = styles[n]
    s.font.name = 'Arial Unicode MS'
    s._element.rPr.rFonts.set(qn('w:ascii'), 'Arial Unicode MS')
    s._element.rPr.rFonts.set(qn('w:hAnsi'), 'Arial Unicode MS')
    s._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Unicode MS')
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = RGBColor.from_string(color)
    s.paragraph_format.space_before = Pt(before)
    s.paragraph_format.space_after = Pt(after)
    s.paragraph_format.keep_with_next = True

code_style = styles.add_style('Prompt Code', WD_STYLE_TYPE.PARAGRAPH)
code_style.font.name = 'Arial Unicode MS'
code_style._element.rPr.rFonts.set(qn('w:ascii'), 'Arial Unicode MS')
code_style._element.rPr.rFonts.set(qn('w:hAnsi'), 'Arial Unicode MS')
code_style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Unicode MS')
code_style.font.size = Pt(8.6)
code_style.paragraph_format.space_after = Pt(4)
code_style.paragraph_format.line_spacing = 1.08

header = sec.header.paragraphs[0]
header.text = 'M-001 IMAGINE｜分镜与提示词操作手册'
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
for r in header.runs:
    r.font.name='Arial Unicode MS'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'Arial Unicode MS'); r.font.size=Pt(8); r.font.color.rgb=RGBColor(110,110,110)

footer = sec.footer.paragraphs[0]
footer.text = '重制整理版｜2026-09-02'
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in footer.runs:
    r.font.name='Arial Unicode MS'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'Arial Unicode MS'); r.font.size=Pt(8); r.font.color.rgb=RGBColor(120,120,120)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(70)
p.paragraph_format.space_after = Pt(10)
r = p.add_run('M-001 Imagine')
r.font.name='Arial Unicode MS'; r._element.rPr.rFonts.set(qn('w:ascii'),'Arial Unicode MS'); r._element.rPr.rFonts.set(qn('w:hAnsi'),'Arial Unicode MS'); r._element.rPr.rFonts.set(qn('w:eastAsia'),'Arial Unicode MS'); r.font.size=Pt(30); r.font.bold=True; r.font.color.rgb=RGBColor.from_string('17324D')
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(28)
r = p.add_run('完整分镜、逐步提示词与剪辑验收规范')
r.font.name='Arial Unicode MS'; r._element.rPr.rFonts.set(qn('w:ascii'),'Arial Unicode MS'); r._element.rPr.rFonts.set(qn('w:hAnsi'),'Arial Unicode MS'); r._element.rPr.rFonts.set(qn('w:eastAsia'),'Arial Unicode MS'); r.font.size=Pt(15); r.font.color.rgb=RGBColor.from_string('486780')

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('交付内容')
r.bold=True; r.font.size=Pt(11); r.font.color.rgb=RGBColor.from_string('B07918')
for line in ['16 张分镜与关键帧', '00–15 全流程可复制提示词', '三段视频生成规范', '15 秒剪辑时间线与四轨滚轮参数', '逐帧身份 / 姿态 / 配件验收清单']:
    p=doc.add_paragraph(style='List Bullet'); p.alignment=WD_ALIGN_PARAGRAPH.LEFT; p.paragraph_format.left_indent=Inches(1.45); p.add_run(line)
doc.add_page_break()

doc.add_heading('1｜分镜总览', level=1)
doc.add_paragraph('以下图片按最终文件命名排列。图片文件同时保存在桌面交付文件夹的“01-分镜图片”子目录。')
for i in range(0, len(image_names), 2):
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    for j in range(2):
        cell = table.cell(0,j)
        cell.width = Inches(3.28)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if i+j < len(image_names):
            name=image_names[i+j]; path=IMG_DIR/name
            pp=cell.paragraphs[0]; pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if path.exists(): pp.add_run().add_picture(str(path), width=Inches(2.55))
            cap=cell.add_paragraph(); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
            rr=cap.add_run(name); rr.font.size=Pt(8.5); rr.bold=True; rr.font.color.rgb=RGBColor.from_string('324A5F')
    if i not in (0,):
        table.rows[0]._tr.get_or_add_trPr()
    if i % 4 == 2 and i < len(image_names)-2:
        doc.add_page_break()
    else:
        doc.add_paragraph().paragraph_format.space_after=Pt(2)

doc.add_page_break()
doc.add_heading('2｜原始逐步生成指令（完整保留）', level=1)
in_code=False
for raw in source_text.splitlines():
    line=raw.rstrip()
    if line.startswith('```'):
        in_code=not in_code
        continue
    if not line:
        doc.add_paragraph('')
    elif line.startswith('### '):
        doc.add_heading(line[4:], level=3)
    elif line.startswith('## '):
        doc.add_heading(line[3:], level=2)
    elif line.startswith('# '):
        doc.add_heading(line[2:], level=1)
    elif line.startswith('- '):
        doc.add_paragraph(line[2:], style='List Bullet')
    else:
        doc.add_paragraph(line, style='Prompt Code' if in_code else 'Normal')

doc.add_page_break()
doc.add_heading('3｜补充制作规范与遗漏项', level=1)
for raw in supplement.splitlines():
    line=raw.rstrip()
    if not line or line in ('---',):
        continue
    if line.startswith('# '):
        continue
    if line.startswith('## '):
        doc.add_heading(line[3:], level=2)
    elif line.startswith('- '):
        doc.add_paragraph(line[2:], style='List Bullet')
    elif len(line)>2 and line[0].isdigit() and line[1]=='.':
        doc.add_paragraph(line[3:], style='List Number')
    else:
        doc.add_paragraph(line)

doc.add_page_break()
doc.add_heading('4｜最终开工前检查表', level=1)
checks = [
    '身份锚点文件正确，且始终排在参考图第一位。','00 与 03 已通过脸、手势、脚位和顶部安全区检查。','04–15 快切预览时眼睛、鼻尖、肩线、手和鞋底无明显位移。','草帽、斜挎包、首饰只出现在指定帧。','01、02、03、15 均为干净单帧，不是拼贴图或旧项目素材。','三段视频关闭生成音频，开场/跳出/结尾首尾帧连续。','四轨使用真实服装缩略图，不使用文字卡，并位于顶部安全区。','所有切换为硬切；局部白闪 1 帧；衣边残影 1 帧且不覆盖脸手。','最终 720×1280、30fps、15.00s，关键切点已逐帧审查。'
]
for c in checks:
    p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(0.15); p.paragraph_format.space_after=Pt(7)
    r=p.add_run('☐  '); r.font.size=Pt(13); r.font.color.rgb=RGBColor.from_string('B07918')
    p.add_run(c)

doc.save(DOCX)
print(DOCX)
print(MD)
