// 创建右键菜单
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "save-as-html",
    title: "保存选中内容为网页文件",
    contexts: ["selection"]
  });
});

// 处理右键菜单点击
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "save-as-html") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: captureAndDownload,
      args: [tab.title, tab.url]
    });
  }
});

// 注入到页面中执行
function captureAndDownload(pageTitle, pageUrl) {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return;

  const range = selection.getRangeAt(0);

  // ---- 1. 定位选区覆盖的最小公共祖先元素 ----
  let ancestor = range.commonAncestorContainer;
  if (ancestor.nodeType === Node.TEXT_NODE) {
    ancestor = ancestor.parentElement;
  }
  if (ancestor === document.body || ancestor === document.documentElement) {
    ancestor = document.body;
  }

  // ---- 2. 深拷贝选区祖先 ----
  const cloned = ancestor.cloneNode(true);

  // ---- 辅助：安全地拼接样式值（双引号→单引号） ----
  function safeVal(v) {
    return v ? v.replace(/"/g, "'") : v;
  }

  // ---- 辅助：解析 px 值 ----
  function parsePx(v) {
    const m = v && v.match(/^([\d.]+)px$/);
    return m ? parseFloat(m[1]) : 0;
  }

  // ---- 3. 内联样式（用于选区内部元素） ----
  function getInlineStyle(el) {
    const cs = window.getComputedStyle(el);
    const props = [
      "font-family", "font-size", "font-weight", "font-style", "font-variant",
      "line-height", "letter-spacing", "word-spacing", "text-align", "text-decoration",
      "text-transform", "text-indent", "text-overflow", "white-space", "word-break",
      "overflow-wrap", "color", "direction",
      "background-color", "background-image", "background-size",
      "background-position", "background-repeat",
      "display", "box-sizing",
      "margin-top", "margin-right", "margin-bottom", "margin-left",
      "padding-top", "padding-right", "padding-bottom", "padding-left",
      "border-top-width", "border-top-style", "border-top-color",
      "border-right-width", "border-right-style", "border-right-color",
      "border-bottom-width", "border-bottom-style", "border-bottom-color",
      "border-left-width", "border-left-style", "border-left-color",
      "border-radius",
      "max-width",
      "float", "clear", "vertical-align", "overflow",
      "flex-direction", "flex-wrap", "justify-content", "align-items", "align-content",
      "gap", "row-gap", "column-gap",
      "flex-grow", "flex-shrink", "flex-basis", "align-self", "order",
      "grid-template-columns", "grid-template-rows", "grid-auto-flow",
      "grid-column", "grid-row",
      "list-style-type", "list-style-position", "list-style-image",
      "border-collapse", "border-spacing", "table-layout",
      "opacity", "box-shadow", "text-shadow", "visibility",
      "cursor", "outline"
    ];

    const parts = [];
    for (const p of props) {
      const v = cs.getPropertyValue(p);
      if (v) parts.push(p + ":" + safeVal(v));
    }

    // min-width / min-height：限制最大值，避免页面容器的巨大值
    const minW = cs.getPropertyValue("min-width");
    if (minW && minW !== "auto" && minW !== "0px") {
      const px = parsePx(minW);
      if (px > 0 && px <= 800) parts.push("min-width:" + safeVal(minW));
    }
    const minH = cs.getPropertyValue("min-height");
    if (minH && minH !== "auto" && minH !== "0px") {
      const px = parsePx(minH);
      if (px > 0 && px <= 800) parts.push("min-height:" + safeVal(minH));
    }

    // position：只保留 static/relative
    const pos = cs.getPropertyValue("position");
    if (pos === "static" || pos === "relative") {
      parts.push("position:" + pos);
    } else {
      parts.push("position:static");
    }

    return parts.join(";");
  }

  // ---- 4. 祖先链精简样式（只保留布局关键属性，不保留尺寸/颜色等） ----
  function getAncestorStyle(el) {
    const cs = window.getComputedStyle(el);
    const parts = [];
    // 只保留布局类属性
    for (const p of [
      "display", "box-sizing",
      "flex-direction", "flex-wrap", "justify-content", "align-items", "align-content",
      "gap", "row-gap", "column-gap",
      "grid-template-columns", "grid-template-rows", "grid-auto-flow",
      "max-width",
      "padding-top", "padding-right", "padding-bottom", "padding-left",
      "margin-top", "margin-right", "margin-bottom", "margin-left"
    ]) {
      const v = cs.getPropertyValue(p);
      if (v) parts.push(p + ":" + safeVal(v));
    }
    parts.push("position:static");
    return parts.join(";");
  }

  // ---- 5. 图片元素样式 ----
  function getImgStyle(el) {
    const cs = window.getComputedStyle(el);
    const parts = [];
    for (const p of [
      "margin-top", "margin-right", "margin-bottom", "margin-left",
      "padding-top", "padding-right", "padding-bottom", "padding-left",
      "border-top-width", "border-top-style", "border-top-color",
      "border-right-width", "border-right-style", "border-right-color",
      "border-bottom-width", "border-bottom-style", "border-bottom-color",
      "border-left-width", "border-left-style", "border-left-color",
      "border-radius", "box-shadow", "opacity", "vertical-align",
      "display"
    ]) {
      const v = cs.getPropertyValue(p);
      if (v) parts.push(p + ":" + safeVal(v));
    }
    parts.push("max-width:100%");
    parts.push("height:auto");
    return parts.join(";");
  }

  // ---- 6. 递归内联样式 ----
  function inlineStyles(orig, clone) {
    if (orig.nodeType !== Node.ELEMENT_NODE) return;

    const cs = window.getComputedStyle(orig);

    if (orig.tagName === "IMG") {
      const opacity = parseFloat(cs.getPropertyValue("opacity"));
      const position = cs.getPropertyValue("position");
      const zIndex = cs.getPropertyValue("z-index");
      const classList = orig.className || "";
      // 检测 X/Twitter 的隐藏占位 img：opacity:0, position:absolute, z-index:-1, 或有 css-9pa8cd 类
      const isHidden = opacity < 0.1 || (position === "absolute" && parseInt(zIndex) < 0) || classList.includes("css-9pa8cd");

      if (isHidden) {
        const src = clone.getAttribute("src") || "";
        if (src) {
          // 恢复可见：移除隐藏类，用 !important 强制显示
          clone.className = (clone.className || "").replace(/css-9pa8cd/g, "").trim();
          clone.setAttribute("style",
            "display:block !important;opacity:1 !important;position:static !important;" +
            "z-index:auto !important;max-width:100%;height:auto;margin:4px 0;" +
            "border-radius:" + cs.getPropertyValue("border-radius")
          );
          clone.removeAttribute("width");
          clone.removeAttribute("height");
        } else {
          clone.setAttribute("style", "display:none");
        }
      } else {
        clone.setAttribute("style", getImgStyle(orig));
      }
    } else {
      const style = getInlineStyle(orig);
      const bgImage = cs.getPropertyValue("background-image");

      if (bgImage && bgImage !== "none" && !bgImage.startsWith("linear-gradient") && !bgImage.startsWith("radial-gradient")) {
        const rect = orig.getBoundingClientRect();
        const extraParts = [];
        if (rect.width > 0 && rect.width < 1200) {
          extraParts.push("width:" + rect.width + "px");
        }
        if (rect.height > 0 && rect.height < 1200) {
          extraParts.push("height:" + rect.height + "px");
        }
        extraParts.push("max-width:100%");
        if (rect.width > 0 && rect.height > 0 && rect.height < 1200) {
          extraParts.push("aspect-ratio:" + (rect.width / rect.height).toFixed(4));
        }
        clone.setAttribute("style", style + ";" + extraParts.join(";"));
      } else {
        if (style) clone.setAttribute("style", style);
      }
    }

    const origChildren = orig.children;
    const cloneChildren = clone.children;
    const len = Math.min(origChildren.length, cloneChildren.length);
    for (let i = 0; i < len; i++) {
      inlineStyles(origChildren[i], cloneChildren[i]);
    }
  }

  inlineStyles(ancestor, cloned);

  // ---- 7. 提取页面样式表中的 CSS 规则（过滤掉会隐藏图片的规则） ----
  function extractPageCSS() {
    const cssTexts = [];
    // 需要过滤掉的隐藏类（如 css-9pa8cd）
    const hiddenClassPattern = /\.css-9pa8cd\b/;
    try {
      for (const sheet of document.styleSheets) {
        try {
          const rules = sheet.cssRules || sheet.rules;
          if (!rules) continue;
          for (const rule of rules) {
            const text = rule.cssText;
            // 跳过会将 img 隐藏的 CSS 规则
            if (hiddenClassPattern.test(text)) continue;
            cssTexts.push(text);
          }
        } catch (e) {}
      }
    } catch (e) {}
    return cssTexts.join("\n");
  }

  const pageCSS = extractPageCSS();

  // ---- 8. 向上收集祖先链（精简样式） ----
  const ancestorChain = [];
  let cur = ancestor.parentElement;
  while (cur && cur !== document.documentElement) {
    ancestorChain.push({
      tag: cur.tagName.toLowerCase(),
      style: cur !== document.body ? getAncestorStyle(cur) : ""
    });
    cur = cur.parentElement;
  }

  let innerHtml = cloned.outerHTML;
  for (const info of ancestorChain) {
    if (info.tag === "body" || info.tag === "html") continue;
    const st = info.style ? ` style="${info.style}"` : "";
    innerHtml = `<${info.tag}${st}>${innerHtml}</${info.tag}>`;
  }

  const wrapper = document.createElement("div");
  wrapper.innerHTML = innerHtml;

  // ---- 9. 图片和链接处理 ----
  wrapper.querySelectorAll("a[href]").forEach((a) => {
    try {
      const href = a.getAttribute("href");
      if (href && !href.startsWith("http") && !href.startsWith("//") && !href.startsWith("#") && !href.startsWith("data:")) {
        a.setAttribute("href", new URL(href, pageUrl).href);
      }
    } catch (_) {}
  });

  function convertImg(imgEl) {
    return new Promise((resolve) => {
      let src = imgEl.getAttribute("src") || "";
      if (!src || src.startsWith("data:")) { resolve(); return; }
      try { src = new URL(src, pageUrl).href; } catch (_) {}

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        try {
          const c = document.createElement("canvas");
          c.width = img.naturalWidth;
          c.height = img.naturalHeight;
          c.getContext("2d").drawImage(img, 0, 0);
          imgEl.setAttribute("src", c.toDataURL("image/png"));
        } catch (e) {
          imgEl.setAttribute("src", src);
        }
        resolve();
      };
      img.onerror = () => { imgEl.setAttribute("src", src); resolve(); };
      img.src = src;
    });
  }

  // 背景图 url 转绝对路径
  wrapper.querySelectorAll("*").forEach((el) => {
    const s = el.getAttribute("style") || "";
    if (s.includes("url(")) {
      el.setAttribute("style", s.replace(
        /url\(["']?(?!data:)((?:(?!["')]).)*)["']?\)/g,
        (m, u) => {
          try { return 'url("' + new URL(u.trim(), pageUrl).href + '")'; }
          catch (_) { return m; }
        }
      ));
    }
  });

  // 背景图也尝试转 base64
  function convertBgImage(el) {
    return new Promise((resolve) => {
      const s = el.getAttribute("style") || "";
      const match = s.match(/background-image:\s*url\(["']?(https?:\/\/[^"')]+)["']?\)/);
      if (!match) { resolve(); return; }
      const bgUrl = match[1];

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        try {
          const c = document.createElement("canvas");
          c.width = img.naturalWidth;
          c.height = img.naturalHeight;
          c.getContext("2d").drawImage(img, 0, 0);
          const dataUrl = c.toDataURL("image/jpeg", 0.9);
          const newStyle = s
            .replace(/background-image:\s*url\(["']?[^"')]+["']?\)/, 'background-image:url("' + dataUrl + '")')
            .replace(/background:\s*[^;]*url\(["']?[^"')]+["']?\)[^;]*/, (bgMatch) => {
              return bgMatch.replace(/url\(["']?[^"')]+["']?\)/, 'url("' + dataUrl + '")');
            });
          el.setAttribute("style", newStyle);
        } catch (e) {}
        resolve();
      };
      img.onerror = () => resolve();
      img.src = bgUrl;
    });
  }

  const bgElements = Array.from(wrapper.querySelectorAll("*")).filter((el) => {
    const s = el.getAttribute("style") || "";
    return s.includes("background-image") && s.includes("url(") && !s.includes("data:");
  });

  const imgPromises = Array.from(wrapper.querySelectorAll("img")).map(convertImg);
  const bgPromises = bgElements.map(convertBgImage);

  Promise.all([...imgPromises, ...bgPromises]).then(() => {
    const now = new Date();
    const dateStr = [
      now.getFullYear(),
      String(now.getMonth() + 1).padStart(2, "0"),
      String(now.getDate()).padStart(2, "0")
    ].join("-") + " " + [
      String(now.getHours()).padStart(2, "0"),
      String(now.getMinutes()).padStart(2, "0")
    ].join(":");

    const finalHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${pageTitle} - 摘录</title>
<style>
/* 原始页面样式 */
${pageCSS}

/* 覆盖修复 */
body {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px;
  background: #fff;
}
.capture-source-info {
  background: #f8f9fa;
  border-left: 4px solid #4285f4;
  padding: 12px 16px;
  margin-bottom: 24px;
  font-size: 13px;
  color: #666;
  border-radius: 0 6px 6px 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
}
.capture-source-info a { color: #4285f4; text-decoration: none; }
.capture-source-info a:hover { text-decoration: underline; }
hr.capture-divider { border: none; border-top: 1px solid #e0e0e0; margin: 0 0 24px 0; }
/* 强制覆盖隐藏图片的类 */
.capture-content .css-9pa8cd {
  opacity: 1 !important;
  position: static !important;
  z-index: auto !important;
  width: auto !important;
  height: auto !important;
  inset: auto !important;
}
/* 图片防溢出 */
.capture-content img {
  max-width: 100% !important;
  height: auto !important;
  opacity: 1 !important;
  position: static !important;
  z-index: auto !important;
  display: inline-block !important;
}
.capture-content img[style*="display:none"] { display: none !important; }
/* 背景图容器保证可见 */
.capture-content [style*="background-image"] {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
}
/* 防止祖先链/页面容器超大高度 */
.capture-content * {
  min-height: auto !important;
  max-height: none !important;
}
.capture-content [style*="background-image"] {
  min-height: 0 !important;
}
@media print { body { padding: 0; max-width: 100%; } }
</style>
</head>
<body>
  <div class="capture-source-info">
    来源：<a href="${pageUrl}" target="_blank">${pageTitle}</a><br>
    保存时间：${dateStr}
  </div>
  <hr class="capture-divider">
  <div class="capture-content">
    ${wrapper.innerHTML}
  </div>
</body>
</html>`;

    const safeName = pageTitle.replace(/[<>:"/\\|?*]/g, "").replace(/\s+/g, "_").substring(0, 50);
    const blob = new Blob([finalHtml], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = safeName + ".html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}
