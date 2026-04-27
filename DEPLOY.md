# 陌拜地图 - 部署指南

## 方式一：Vercel 部署（推荐）

### 1. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`field-map`
3. 选择 **Public** 或 **Private**
4. 点击 **Create repository**

### 2. 推送代码到 GitHub

```bash
cd /Users/pl1688/WorkBuddy/20260425092842/field-map

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/field-map.git

# 推送代码
git branch -M main
git push -u origin main
```

### 3. 部署到 Vercel

1. 访问 https://vercel.com/new
2. 点击 **Import Git Repository**
3. 选择 `field-map` 仓库
4. 框架预设选择 **Other**
5. 点击 **Deploy**

部署完成后，Vercel 会提供一个 `.vercel.app` 域名，例如：
`https://field-map-xxx.vercel.app`

---

## 方式二：GitHub Pages 部署

### 1. 推送代码到 GitHub（同上）

### 2. 启用 GitHub Pages

1. 进入 GitHub 仓库 → **Settings** → **Pages**
2. **Source** 选择 **Deploy from a branch**
3. **Branch** 选择 **main** / **root**
4. 点击 **Save**

几分钟后，访问 `https://YOUR_USERNAME.github.io/field-map/`

---

## ⚠️ 重要：高德地图 Key 配置

部署后，**必须**替换高德地图 Key，否则地图无法显示。

### 1. 申请高德地图 Key

1. 访问 https://lbs.amap.com/dev/key/app
2. 登录/注册账号
3. 创建新应用 → 添加 Key
4. **服务平台** 选择 **Web端(JS API)**
5. 复制生成的 Key

### 2. 替换代码中的 Key

编辑 `index.html`，找到第 7 行：

```html
<script src="https://webapi.amap.com/maps?v=2.0&key=YOUR_AMAP_KEY&plugin=...">
```

替换 `YOUR_AMAP_KEY` 为你申请的高德 Key。

### 3. 重新部署

```bash
git add index.html
git commit -m "更新高德地图 Key"
git push
```

---

## 部署验证清单

- [ ] 页面能正常加载
- [ ] 地图能正常显示
- [ ] 定位功能正常
- [ ] 搜索附近场所正常
- [ ] 添加标注正常
- [ ] 数据能正常保存

---

## 常见问题

### Q: 地图显示空白？
A: 检查高德 Key 是否正确，以及 Key 的 **服务平台** 是否为 **Web端(JS API)**。

### Q: 定位失败？
A: 确保网站使用 HTTPS（Vercel/GitHub Pages 默认支持），且用户授权了定位权限。

### Q: 如何更新应用？
A: 修改代码后执行 `git add . && git commit -m "更新说明" && git push`，Vercel 会自动重新部署。
