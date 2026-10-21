# 桌游规则网页：更新与重新部署说明

## 文件结构
- `src/head.html` —— `<head>` 和全部 CSS（手机优先，深色模式自动）。
- `src/NN-<游戏>.html` —— 每款游戏一个片段，按文件名数字排序（10 小小城镇、20 矮人矿坑、30 卡坦岛、40 快餐连锁大亨、50 骰子街、60 北境之地、70 现在下午五点）。
- `build.py` —— 把 head + 所有片段拼成 `index.html`，**自动生成**顶部吸顶导航、目录、每款游戏的章节小标签和“最后更新”时间（Asia/Shanghai）。
- `index.html` —— 生成结果（单文件、无外部资源、无图片）。不要手改，改 `src/` 后重新 build。
- `deploy.sh` —— 匿名发布到 here.now。
- `.herenow-state*.json` —— 发布返回的 claimToken/claimUrl（权限 600，**绝不能放进网页或公开**）。

## 新增/更新一款游戏
1. 先在 `/workspace/boardgames/<游戏>/rules-summary.md` 写好摘要（网页内容只能来自摘要文件，保留 ⚠️/推断/可信度标记）。
2. 复制一个现有片段，例如 `cp src/60-northgard.html src/80-newgame.html`，改：
   - `<section class="game" id="短id" data-short="导航短名">`（id 全站唯一，只用字母数字）；
   - `<h2>` 标题，状态标签用 `<span class="ok">完整</span>` / `<span class="part">…</span>` / `<span class="todo">待补</span>`；
   - 六个固定小节，`<h3 id="短id-info|play|rules|score|penalty|faq|src">`：基本信息、核心玩法/回合流程、建筑/模块/卡牌规则、得分方式、扣分/惩罚规则、常见误区/待核实，加“来源”。
   - 表格外面包 `<div class="tw">…</div>` 以便手机横向滚动；重点用 `<div class="hl">`，警告用 `<div class="warn">`。
3. `python3 build.py`（会打印字节数、游戏数、时间）。
4. 自检：锚点、标签闭合、无密钥（可用 build 后的 python 片段，或手机宽度截图：
   `google-chrome --headless --no-sandbox --window-size=390,2400 --screenshot=/tmp/m.png file://$PWD/index.html`）。
5. **版权**：不要嵌入或上传规则书 PDF、规则书照片、卡图；只放文字摘要和外链。

## 重新部署
- `./deploy.sh` —— here.now 匿名发布：无需账号、免费，**24 小时后过期，且每次都是新网址**（匿名限速约 5 次/小时/IP）。脚本最后用 curl 确认 HTTP 200。
- 想要固定网址、永久保存：打开当次发布返回的 claimUrl 认领（需要一个 here.now 账号/邮箱；要不要用俊伟自己的邮箱须先问他）。认领后用 API key 更新同一个站点。
- 其他已试/可选方案：
  - Netlify 匿名部署 `npx netlify-cli deploy --allow-anonymous --dir=… --no-build`：无需账号，但 **1 小时内不认领就删除**；2026-10-22 试时本机 IP 已达“每日匿名部署上限”。
  - surge.sh、Cloudflare Pages（wrangler）、Neocities、Vercel：都需要登录/注册账号。
  - GitHub Pages：按要求不使用（需要另一个 bot 和俊伟批准）。

## 当前部署记录
- 2026-10-22 02:56（北京时间）发布：https://graceful-rivulet-q4z8.here.now/ ，过期 2026-10-23 02:56（北京时间）。认领信息在 `.herenow-state.json`。
