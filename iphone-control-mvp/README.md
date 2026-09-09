# iPhone Control MVP

这个项目通过 Codex 管理自己的本地发布控制器：Mac 同时识别多台真实 iPhone，并通过网页为指定 UDID 建立独立的 Appium/XCUITest session，或只在该设备上启动已经安装的抖音 App。

项目不会依赖 EasyClick 的内置工作流。素材领取和发布记录由本项目的 SQLite 台账负责；手机 UI 操作由每台设备独立的 Appium/WDA 会话执行。

## AutoDL.Art 视频生成

在 `.env` 中设置 `AUTODL_COMFYUI_TOKEN`（令牌分组必须选择 `ComfyUI`）。通过以下接口提交并查询任意 AutoDL ComfyUI 视频工作流：

- `POST /api/video-generation/tasks`：请求体为 `{"workflow_id":"...","parameters":{...}}`。
- `GET /api/video-generation/tasks/{task_id}?refresh=true`：查询 AutoDL 最新状态；成功后立即下载视频。
- `GET /api/video-generation/tasks`：查看本地持久化的生成任务。

不同工作流的 `parameters` 不同，以 AutoDL 工作流页面“在线调用 API”展示的请求体为准。成功视频保存为 `PUBLISHER_INBOX/autodl-{task_id}.mp4`，因此会自动进入现有发布素材台账。任务和参数记录在 `data/video_generation.sqlite3`，Token 不会写入数据库。

## 发布控制器（防重底座）

把待发布的 mp4 放在 `PUBLISHER_INBOX`（默认
`/Users/apple/Desktop/素材/inbox`）。每个视频可以附一个同名元数据文件，例如
`video.mp4.json`：

```json
{
  "caption": "今天的片段分享给你",
  "tags": ["#记录生活", "#日常"],
  "effect": "已校准的特效名",
  "bgm": "已校准的 BGM 名"
}
```

发布器先通过 `POST /api/publisher/claim` 为一个 UDID 原子领取视频。其状态为
`leased → prepared → published`；任何不确定结果必须写入 `needs_review`，不会被另一台
手机重新领取。即使 20 台设备同时请求，SQLite 的 `BEGIN IMMEDIATE` 事务也只会让其中一台
获得同一个素材。

当前提供的接口：

- `GET /api/publisher/assets`：查看素材台账。
- `POST /api/publisher/claim`：领取一条未发布素材。
- `POST /api/publisher/{run_id}/prepared`：素材已导入并到达发布前确认页。
- `POST /api/publisher/{run_id}/published`：仅在检测到抖音发布成功页后标记已发布。
- `POST /api/publisher/{run_id}/needs-review`：页面异常或网络失败时冻结素材。

每台手机的 UI 定位保存在 `calibrations/<UDID>.json`。先复制
`00008120-000E113E3628C01E.example.json`，再用 Appium Inspector 填入这台手机的真实
可访问性标签；不要把坐标或标签混用到另一台设备。校准期必须保留
`pause_before_publish`，连续三次确认发布成功后才可把该步骤替换为自动发布。

## 1. 架构与隔离原则

- `DeviceManager` 通过 `libimobiledevice` 的 `idevice_id` 枚举 USB/已配对设备，再通过 `ideviceinfo` 读取设备名称。
- 所有操作的 URL 都包含完整 UDID；后端执行前会重新确认该 UDID 仍在线。
- `AppiumManager` 按 UDID 保存独立 driver 和异步锁。
- 每台设备获得唯一的 `wdaLocalPort`、`mjpegServerPort` 和 `derivedDataPath`。
- “打开抖音”只在该 UDID 对应 driver 上调用当前 XCUITest 扩展 `mobile: launchApp`，随后用 `mobile: queryAppState` 确认应用处于前台。
- Appium session 保持到服务关闭，以便分别维持两台设备的 WDA 连接。

官方资料：

- [Appium XCUITest 真机配置](https://appium.github.io/appium-xcuitest-driver/latest/preparation/real-device-config/)
- [XCUITest capabilities](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/)
- [XCUITest 并行测试](https://appium.github.io/appium-xcuitest-driver/latest/guides/parallel-tests/)
- [Apple：开启 Developer Mode](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)

## 2. 从全新 Mac 开始安装

以下命令在 Apple Silicon Mac 上执行。Intel Mac 的 Homebrew 默认路径不同，但通过 `brew` 命令安装后的使用方式相同。

### 2.1 安装 Homebrew

打开“终端”，执行 Homebrew 官网提供的安装命令：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安装器结束时会显示一到两行用于把 Homebrew 加入 `PATH` 的命令，按终端提示执行。验证：

```bash
brew --version
```

### 2.2 安装完整 Xcode

必须安装完整 Xcode，只有 Command Line Tools 不够。可从 Mac App Store 安装 Xcode，也可从 [Apple Developer Downloads](https://developer.apple.com/download/all/) 下载与当前 macOS/iOS 兼容的版本。

首次打开 Xcode，等待附加组件安装完成。然后执行：

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
sudo xcodebuild -runFirstLaunch
xcodebuild -version
```

如果 Xcode App 不叫 `Xcode.app`，把路径替换成实际名称。`xcode-select -p` 的结果必须指向 Xcode App 内部，不能停留在 `/Library/Developer/CommandLineTools`。

在 Xcode 中打开 `Xcode > Settings > Accounts`，登录用于签名的 Apple ID。建议使用 Apple Developer Program 团队。Team ID 是 10 位字符串，可在 Apple Developer 账号的 Membership 页面查看。

### 2.3 安装 Python、Node.js 和 iPhone 命令行工具

```bash
brew install python node libimobiledevice ideviceinstaller
python3 --version
node --version
npm --version
idevice_id --version
```

### 2.4 安装 Appium 和 XCUITest driver

```bash
npm install --global appium
appium --version
appium driver install xcuitest
appium driver list --installed
appium driver doctor xcuitest
```

如果 `npm install --global` 成功但终端找不到 `appium`，先执行 `npm config get prefix`，把该目录下的 `bin` 加入 shell 的 `PATH`，然后重新打开终端。

当前项目搭建时实际安装并验证的版本是 Appium `3.7.0` 和 XCUITest driver `12.8.2`。不要求永远固定这两个全局版本，但升级后应重新执行 doctor 和实机验收。

## 3. 准备每台 iPhone

两台手机都要分别完成以下步骤：

1. 用支持数据传输的 USB 线连接 Mac，暂时不要从无线配对开始。
2. 解锁 iPhone；出现“要信任此电脑吗？”时点击“信任”，输入设备密码。
3. 在 Finder 侧边栏选中 iPhone。如出现信任提示，再次确认。
4. 在 Xcode 打开 `Window > Devices and Simulators`，等待设备准备完成且没有黄色错误。
5. 在 iPhone 打开 `设置 > 隐私与安全性 > 开发者模式`，开启后按提示重启。
6. 重启解锁后再次确认开启 Developer Mode，并输入设备密码。
7. 保持抖音已通过 App Store 正常安装。项目不会代替安装抖音。

如果“开发者模式”尚未出现，先让 Xcode 与设备完成一次配对，再回到“隐私与安全性”查看。

验证 libimobiledevice 能看到设备：

```bash
idevice_id -l
```

连接两台时必须返回两行不同 UDID。分别读取名称：

```bash
ideviceinfo -u "第一台UDID" -k DeviceName
ideviceinfo -u "第二台UDID" -k DeviceName
```

再验证 Appium driver 的设备枚举：

```bash
appium driver run xcuitest list-real-devices
```

若 `idevice_id` 没结果，先排查数据线、USB Hub、设备是否解锁和“信任此电脑”，不要继续排查 WDA。

## 4. WebDriverAgent 签名

WDA 是实际运行在 iPhone 上的 XCTest runner，因此每台真机都必须允许你的开发团队签名并运行它。

### 4.1 推荐：由 Appium 自动配置签名

复制配置文件后填写：

```bash
cp .env.example .env
```

至少修改：

```dotenv
XCODE_ORG_ID=你的10位TeamID
XCODE_SIGNING_ID="Apple Development"
WDA_BUNDLE_ID=com.你的反向域名.WebDriverAgentRunner
```

`WDA_BUNDLE_ID` 必须对你的团队唯一，例如 `com.example.myteam.WebDriverAgentRunner`，不要照抄示例。项目会把这些值作为 `xcodeOrgId`、`xcodeSigningId` 和 `updatedWDABundleId` 传给 XCUITest driver，并允许 Xcode 更新 provisioning profile 和注册设备。

第一次建立 session 会编译 WDA，可能需要一到数分钟。终端会打印完整 Xcode/Appium 日志。

### 4.2 自动签名失败时：在 Xcode 检查 WDA 工程

打开当前 driver 自带的 WDA 工程：

```bash
appium driver run xcuitest open-wda
```

在 Xcode 中：

1. 选择 `WebDriverAgent` 工程。
2. 检查 `WebDriverAgentRunner` target 的 `Signing & Capabilities`。
3. 勾选 `Automatically manage signing`。
4. Team 选择与 `.env` 中 `XCODE_ORG_ID` 相同的团队。
5. Bundle Identifier 使用属于该团队的唯一标识；它应与 `.env` 中 `WDA_BUNDLE_ID` 对应。XCTest 构建时会使用 `.xctrunner` 后缀。
6. 如当前 WDA 工程还展示其他需要签名的 target，也为其选择同一个 Team。
7. Scheme 选择 `WebDriverAgentRunner`，运行目标选择第一台真实 iPhone，然后执行 `Product > Test`。
8. 第一台成功后，把运行目标切换成第二台，再执行一次 `Product > Test`。

若手机提示开发者不受信任，可在 iPhone 的 `设置 > 通用 > VPN与设备管理` 中信任对应开发者；具体入口会随 iOS 版本变化。

成功的表现是 Xcode 测试开始、设备上安装/启动 WebDriverAgentRunner，并且 Xcode 日志不再出现 code signing、provisioning 或 Developer Mode 错误。手动测试完成后停止 Xcode 中的测试，之后由 Appium 启动 WDA。

## 5. 确认抖音 bundle id

中国大陆版抖音常见 bundle id 是 `com.ss.iphone.ugc.Aweme`，但不要仅依赖这个默认值；应从实际设备上的已安装应用读取。

先连接并解锁目标 iPhone，然后执行：

```bash
ideviceinstaller -u "设备UDID" list --user --xml > /tmp/iphone-user-apps.plist
plutil -p /tmp/iphone-user-apps.plist | grep -i -C 4 -E '抖音|Aweme'
```

在对应应用条目中确认 `CFBundleIdentifier`，把值填入 `.env`：

```dotenv
DOUYIN_BUNDLE_ID=实际查询到的值
```

两台设备应安装同一地区/同一产品版本的抖音，并分别查询一次。如果 bundle id 不一致，当前 MVP 的单一 `DOUYIN_BUNDLE_ID` 配置不满足需求，需要先统一安装版本。

## 6. 安装并运行项目

进入项目目录：

```bash
cd "/Users/apple/Documents/ChatGPT/群控/iphone-control-mvp"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，至少确认以下值：

```dotenv
APPIUM_SERVER_URL=http://127.0.0.1:4723
DOUYIN_BUNDLE_ID=com.ss.iphone.ugc.Aweme
XCODE_ORG_ID=你的10位TeamID
XCODE_SIGNING_ID="Apple Development"
WDA_LOCAL_PORT=8100
WDA_BUNDLE_ID=com.你的反向域名.WebDriverAgentRunner
```

启动：

```bash
./start.sh
```

`start.sh` 会在默认地址尚无 Appium 时启动一个本地 Appium Server，然后启动 FastAPI。访问：

```text
http://localhost:8000
```

如果配置了非默认 `APPIUM_SERVER_URL`，需自行先启动对应 Appium Server。

停止服务按 `Control-C`。项目会关闭它持有的所有 Appium session；若 Appium 是由 `start.sh` 启动，也会一并停止。Appium 原始日志位于 `.appium.log`。

## 7. API 和页面行为

- `GET /api/devices`：实时读取当前已连接设备。
- `POST /api/devices/{udid}/test`：为该 UDID 创建或探测独立 WDA session。
- `POST /api/devices/{udid}/open-douyin`：复用或建立该 UDID 的 session，仅调用 `mobile: launchApp` 启动 `DOUYIN_BUNDLE_ID`。

页面每 5 秒刷新设备列表；执行测试连接或启动应用期间会暂停刷新，避免长时间 WDA 构建使结果区域丢失。

终端会记录：发现的设备和 UDID、隔离端口、session 创建结果、WDA 探测结果、抖音启动结果以及失败时的完整 traceback。

## 8. 实机验收顺序

严格按顺序执行；当前一步失败时先修复，不继续：

1. 只连接设备 A。确认 `idevice_id -l` 返回一行，网页显示 A。
2. 再连接设备 B。确认命令返回两行，网页同时显示 A、B。
3. 点击 A 的“测试连接”，记录页面的成功结果和终端中的 A session ID/WDA 端口。
4. 点击 B 的“测试连接”，确认 session ID 与 WDA 端口都不同。
5. 点击 A 的“打开抖音”，肉眼确认只有 A 进入前台，B 保持原界面。
6. 点击 B 的“打开抖音”，肉眼确认只有 B 进入前台。

可用 API 独立复核，其中 UDID 必须做 URL 编码：

```bash
curl http://127.0.0.1:8000/api/devices
curl -X POST "http://127.0.0.1:8000/api/devices/设备A的UDID/test"
curl -X POST "http://127.0.0.1:8000/api/devices/设备B的UDID/test"
curl -X POST "http://127.0.0.1:8000/api/devices/设备A的UDID/open-douyin"
curl -X POST "http://127.0.0.1:8000/api/devices/设备B的UDID/open-douyin"
```

## 9. 常见失败与处理顺序

### 网页没有设备

依次检查 `idevice_id -l`、手机是否解锁、是否信任 Mac、线缆是否支持数据。该问题与 FastAPI/Appium 无关。

### `xcodebuild requires Xcode`

说明只有 Command Line Tools 或 active developer directory 错误：

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -version
```

### WDA 出现 code 65、签名或 provisioning 错误

检查 Xcode 已登录 Apple ID、Team ID 正确、`WDA_BUNDLE_ID` 唯一、两台设备都已注册到团队、Developer Mode 已打开。然后用 `open-wda` 流程分别对两台设备执行 `Product > Test`。

### 8100 端口冲突

修改 `.env` 中 `WDA_LOCAL_PORT` 起始值，例如改为 `8200`。系统会从起始值向上为每台设备找空闲端口；MJPEG 端口从起始值加 1000 后向上分配。

### 测试连接成功但抖音启动失败

使用 `ideviceinstaller` 重新确认该设备上的 bundle id，并确认抖音确实已安装。终端中的完整异常通常会区分“应用不存在”和“应用无法启动”。

### 第二台设备影响第一台

停止服务，确认没有遗留的其他 Appium/WDA 进程占用端口，再查看日志中两台设备的 `udid`、`wdaLocalPort`、`mjpegServerPort`、`derivedDataPath` 是否全部不同。不要把 capability 的 UDID 设置为 `auto`。

## 10. 当前这台 Mac 的实测状态

搭建时已完成：

- Homebrew 可用。
- Python 3.14.6、Node.js 24.17.0 可用。
- 已安装 `libimobiledevice` 和 `ideviceinstaller`。
- 已安装 Appium 3.7.0。
- 已安装并验证 XCUITest driver 12.8.2。
- Python 虚拟环境和项目依赖已安装。

尚未具备的实机条件：

- `/Applications` 中没有完整 Xcode，当前 `xcode-select` 指向 Command Line Tools。
- 检查时 USB 层没有发现已连接的 iPhone。
- `.env` 中还没有你的真实 `XCODE_ORG_ID` 和唯一 `WDA_BUNDLE_ID`。

因此目前可以验证 Web 页面、设备为空时的行为和接口结构，但只有补齐上述三项后才能完成 A–F 真机验收。
