// 创建右键菜单
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "save-clean-html",
    title: "保存选中内容（简洁排版）",
    contexts: ["selection"]
  });
});

// 处理右键菜单点击
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "save-clean-html") return;

  // 第一步：注入脚本提取内容
  const [result] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: extractContent,
    args: [tab.title, tab.url]
  });

  if (!result || !result.result) return;
  const data = result.result;

  // 第二步：在 background 中解析短链接
  const resolvedMap = {};
  if (data.shortUrls && data.shortUrls.length > 0) {
    await Promise.all(data.shortUrls.map(async (entry) => {
      try {
        const resp = await fetch(entry.shortUrl, { method: "HEAD", redirect: "follow" });
        resolvedMap[entry.id] = resp.url || entry.shortUrl;
      } catch (e) {
        try {
          const resp = await fetch(entry.shortUrl, { redirect: "follow" });
          resolvedMap[entry.id] = resp.url || entry.shortUrl;
        } catch (e2) {
          resolvedMap[entry.id] = entry.shortUrl;
        }
      }
    }));
  }

  // 第三步：注入脚本，替换占位符 + 转图片 base64 + 下载
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: finalizeAndDownload,
    args: [data, resolvedMap]
  });
});

// ============================================================
// 第一步：提取内容（在页面上下文运行）
// ============================================================
function extractContent(pageTitle, pageUrl) {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return null;

  const range = selection.getRangeAt(0);
  let ancestor = range.commonAncestorContainer;
  if (ancestor.nodeType === Node.TEXT_NODE) {
    ancestor = ancestor.parentElement;
  }

  const blocks = [];
  const shortUrls = []; // 需要 background 解析的短链接

  function getTextContent(el) {
    return (el.textContent || "").replace(/\s+/g, " ").trim();
  }

  function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function linkifyText(text) {
    const urlRegex = /(https?:\/\/[^\s<>"']+|(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+(?:com|org|net|io|co|dev|app|me|info|xyz|ai|cc|cn|uk|de|fr|jp|ru|br|in|au|ca|us|eu|tech|site|top|club|online|store|space|fun|pro|biz|name|tv|gov|edu|mil|int)(?:\/[^\s<>"']*)?))/gi;
    let result = "";
    let lastIndex = 0;
    let match;
    while ((match = urlRegex.exec(text)) !== null) {
      result += escapeHtml(text.slice(lastIndex, match.index));
      let url = match[0];
      url = url.replace(/[.,;:!?)]+$/, "");
      const absUrl = url.startsWith("http") ? url : "https://" + url;
      result += `<a href="${escapeHtml(absUrl)}" target="_blank">${escapeHtml(url)}</a>`;
      lastIndex = match.index + match[0].length;
      const trimmed = match[0].length - url.length;
      if (trimmed > 0) {
        result += escapeHtml(match[0].slice(match[0].length - trimmed));
      }
    }
    result += escapeHtml(text.slice(lastIndex));
    return result;
  }

  function looksLikeTruncatedUrl(text) {
    if (!text) return false;
    const t = text.trim();
    if (!t.includes("…") && !t.endsWith("...")) return false;
    return /^(https?:\/\/)?[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}/i.test(t);
  }

  function isShortUrl(url) {
    return /^https?:\/\/(t\.co|bit\.ly|goo\.gl|tinyurl\.com|ow\.ly|is\.gd|buff\.ly|adf\.ly|bl\.ink|rb\.gy|cutt\.ly|short\.io)\//i.test(url);
  }

  function getFullUrlFromLinkSync(aEl, absHref) {
    const title = aEl.getAttribute("title");
    if (title && /^https?:\/\//i.test(title)) return title;
    const expanded = aEl.getAttribute("data-expanded-url");
    if (expanded) return expanded;
    const ariaLabel = aEl.getAttribute("aria-label");
    if (ariaLabel && /^https?:\/\//i.test(ariaLabel)) return ariaLabel;
    const allSpans = aEl.querySelectorAll("span");
    for (const span of allSpans) {
      const text = (span.textContent || "").trim();
      if (/^https?:\/\//i.test(text) && !text.includes("…") && !text.endsWith("...") && text.length > 20) return text;
    }
    if (allSpans.length > 0) {
      let combined = "";
      for (const span of allSpans) {
        if (span.querySelectorAll("span").length === 0) combined += (span.textContent || "");
      }
      combined = combined.trim();
      if (combined && /^https?:\/\//i.test(combined) && !combined.includes("…") && !combined.endsWith("...") && combined.length > 20) return combined;
    }
    const ft = (aEl.textContent || "").trim();
    if (ft && /^https?:\/\//i.test(ft) && !ft.includes("…") && !ft.endsWith("...") && ft.length > 20) return ft;
    if (absHref && !isShortUrl(absHref)) return absHref;
    return null;
  }

  function registerShortUrl(shortUrl) {
    const id = "__SHORT_URL_" + shortUrls.length + "__";
    shortUrls.push({ id, shortUrl });
    return id;
  }

  function toAbsUrl(url) {
    if (!url || url.startsWith("data:") || url.startsWith("javascript:")) return url;
    try { return new URL(url, pageUrl).href; } catch (_) { return url; }
  }

  // 富文本提取
  function getRichText(el) {
    let html = "";
    for (const child of el.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) {
        html += linkifyText(child.textContent);
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        const tag = child.tagName;
        if (tag === "BR") {
          html += "<br>";
        } else if (tag === "IMG") {
          // 跳过内联图片（单独处理）
        } else if (tag === "A") {
          const href = child.getAttribute("href") || "";
          const absHref = toAbsUrl(href);
          let inner = getRichText(child);
          const plainInner = inner.replace(/<[^>]*>/g, "").trim();
          if (plainInner && looksLikeTruncatedUrl(plainInner)) {
            const fullUrl = getFullUrlFromLinkSync(child, absHref);
            if (fullUrl && !isShortUrl(fullUrl)) {
              html += `<a href="${escapeHtml(fullUrl)}" target="_blank">${escapeHtml(fullUrl)}</a>`;
            } else {
              // 需要异步解析短链接
              const placeholder = registerShortUrl(absHref);
              html += `<a href="${placeholder}" target="_blank">${placeholder}</a>`;
            }
          } else {
            if (inner) html += `<a href="${escapeHtml(absHref)}" target="_blank">${inner}</a>`;
          }
        } else if (tag === "STRONG" || tag === "B") {
          const inner = getRichText(child);
          if (inner) html += `<strong>${inner}</strong>`;
        } else if (tag === "EM" || tag === "I") {
          const inner = getRichText(child);
          if (inner) html += `<em>${inner}</em>`;
        } else if (tag === "CODE") {
          const inner = getRichText(child);
          if (inner) html += `<code>${inner}</code>`;
        } else if (tag === "DEL" || tag === "S") {
          const inner = getRichText(child);
          if (inner) html += `<del>${inner}</del>`;
        } else if (tag === "U") {
          const inner = getRichText(child);
          if (inner) html += `<u>${inner}</u>`;
        } else if (["SPAN","DIV","P","SECTION","ARTICLE","MAIN","ASIDE","HEADER","FOOTER","NAV","FIGURE","FIGCAPTION","LABEL","SMALL","MARK","SUP","SUB","TIME","ABBR","CITE","DFN","KBD","SAMP","VAR"].includes(tag)) {
          html += getRichText(child);
        } else {
          html += escapeHtml(getTextContent(child));
        }
      }
    }
    return html;
  }

  // 图片相关
  function getVisibleImgSrc(img) {
    let src = img.getAttribute("src") || "";
    if (!src || src === "about:blank" || src.startsWith("data:image/svg") || src.startsWith("data:image/gif") || /^data:image\/[^;]+;base64,.{0,100}$/.test(src)) {
      src = img.getAttribute("data-src")
        || img.getAttribute("data-original")
        || img.getAttribute("data-lazy-src")
        || img.getAttribute("data-origin")
        || img.getAttribute("data-actualsrc")
        || img.getAttribute("data-original-src")
        || img.getAttribute("data-echo")
        || "";
    }
    if (!src || src === "about:blank") {
      const srcset = img.getAttribute("srcset") || "";
      if (srcset) src = getBestSrcFromSrcset(srcset);
    }
    if (!src && img.currentSrc && img.currentSrc !== "about:blank") {
      src = img.currentSrc;
    }
    if (!src && img.parentElement && img.parentElement.tagName === "PICTURE") {
      const sources = img.parentElement.querySelectorAll("source");
      for (const source of sources) {
        const ss = source.getAttribute("srcset") || "";
        if (ss) { src = getBestSrcFromSrcset(ss); break; }
      }
    }
    if (!src || src === "about:blank") {
      src = img.src || "";
    }
    if (!src || src === "about:blank") return null;
    const w = img.naturalWidth || 0;
    const h = img.naturalHeight || 0;
    if (w > 0 && w <= 2 && h > 0 && h <= 2) return null;
    return toAbsUrl(src);
  }

  function getBestSrcFromSrcset(srcset) {
    if (!srcset) return "";
    const parts = srcset.split(",").map((s) => s.trim()).filter(Boolean);
    let bestUrl = "";
    let bestW = 0;
    for (const part of parts) {
      const tokens = part.split(/\s+/);
      if (tokens.length >= 1) {
        const url = tokens[0];
        const descriptor = tokens[1] || "";
        const wMatch = descriptor.match(/(\d+)w/);
        const w = wMatch ? parseInt(wMatch[1]) : 0;
        if (w > bestW || !bestUrl) {
          bestW = w;
          bestUrl = url;
        }
      }
    }
    return bestUrl;
  }

  function getBgImageSrc(el) {
    const cs = window.getComputedStyle(el);
    const bg = cs.getPropertyValue("background-image");
    if (!bg || bg === "none") return null;
    const m = bg.match(/url\(["']?(https?:\/\/[^"')]+)["']?\)/);
    if (!m) return null;
    if (bg.includes("gradient")) return null;
    const rect = el.getBoundingClientRect();
    if (rect.width < 10 || rect.height < 10) return null;
    return m[1];
  }

  function collectImages(el) {
    const srcs = [];
    if (el.tagName === "IMG") {
      const src = getVisibleImgSrc(el);
      if (src) srcs.push(src);
      return srcs;
    }
    if (el.tagName === "PICTURE") {
      const img = el.querySelector("img");
      if (img) { const s = getVisibleImgSrc(img); if (s) srcs.push(s); }
      return srcs;
    }
    el.querySelectorAll("img").forEach((img) => {
      const src = getVisibleImgSrc(img);
      if (src) srcs.push(src);
    });
    el.querySelectorAll("picture").forEach((pic) => {
      const img = pic.querySelector("img");
      if (img) { const s = getVisibleImgSrc(img); if (s) srcs.push(s); }
    });
    el.querySelectorAll("*").forEach((child) => {
      const bgSrc = getBgImageSrc(child);
      if (bgSrc) srcs.push(bgSrc);
    });
    const selfBg = getBgImageSrc(el);
    if (selfBg) srcs.push(selfBg);
    return [...new Set(srcs)];
  }

  // 递归提取内容块
  function extractBlocks(el) {
    if (el.nodeType === Node.TEXT_NODE) {
      const text = el.textContent.trim();
      if (text) blocks.push({ type: "text", html: linkifyText(text) });
      return;
    }
    if (el.nodeType !== Node.ELEMENT_NODE) return;

    const tag = el.tagName;
    const cs = window.getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return;
    if (tag !== "IMG" && parseFloat(cs.opacity) < 0.05) return;

    if (/^H[1-6]$/.test(tag)) {
      const text = getTextContent(el);
      if (text) blocks.push({ type: "heading", level: parseInt(tag[1]), html: getRichText(el) });
      return;
    }
    if (tag === "HR") { blocks.push({ type: "hr" }); return; }
    if (tag === "PRE" || (tag === "CODE" && el.parentElement && el.parentElement.tagName === "PRE")) {
      const code = el.textContent || "";
      if (code.trim()) blocks.push({ type: "code", text: code });
      return;
    }
    if (tag === "BLOCKQUOTE") {
      const text = getRichText(el);
      if (text.trim()) blocks.push({ type: "blockquote", html: text });
      return;
    }
    if (tag === "UL" || tag === "OL") {
      const items = [];
      el.querySelectorAll(":scope > li").forEach((li) => {
        const t = getRichText(li);
        if (t.trim()) items.push(t);
      });
      if (items.length > 0) blocks.push({ type: "list", ordered: tag === "OL", items });
      return;
    }
    if (tag === "VIDEO") {
      const src = el.getAttribute("src") || el.querySelector("source")?.getAttribute("src") || "";
      if (src) blocks.push({ type: "video", src: toAbsUrl(src), poster: el.getAttribute("poster") || "" });
      return;
    }
    if (tag === "IMG") {
      const src = getVisibleImgSrc(el);
      if (src) blocks.push({ type: "image", src, alt: el.getAttribute("alt") || "" });
      return;
    }
    if (tag === "PICTURE") {
      const img = el.querySelector("img");
      if (img) {
        const src = getVisibleImgSrc(img);
        if (src) blocks.push({ type: "image", src, alt: img.getAttribute("alt") || "" });
      }
      return;
    }

    const display = cs.display;
    const isFlexOrGrid = display.includes("flex") || display.includes("grid");
    if (isFlexOrGrid) {
      const images = collectImages(el);
      const text = getTextContent(el);
      if (images.length >= 2 && text.length < images.length * 20) {
        blocks.push({ type: "images", srcs: images });
        return;
      }
    }

    const bgSrc = getBgImageSrc(el);
    if (bgSrc) blocks.push({ type: "image", src: bgSrc, alt: "" });

    if (["P","SPAN","LABEL","TD","TH","FIGCAPTION","SMALL"].includes(tag)) {
      const images = collectImages(el);
      const richText = getRichText(el);
      if (richText.trim()) blocks.push({ type: "text", html: richText });
      images.forEach((src) => blocks.push({ type: "image", src, alt: "" }));
      return;
    }

    if (tag === "TABLE") {
      blocks.push({ type: "table", html: el.outerHTML });
      return;
    }

    if ((tag === "A" && display === "block") || (tag === "A" && display.includes("flex"))) {
      const href = toAbsUrl(el.getAttribute("href") || "");
      const text = getTextContent(el);
      const images = collectImages(el);
      if (images.length > 0) images.forEach((src) => blocks.push({ type: "image", src, alt: text }));
      if (text && href) blocks.push({ type: "link", href, text });
      return;
    }

    for (const child of el.childNodes) extractBlocks(child);
  }

  extractBlocks(ancestor);

  // 去重合并
  const mergedBlocks = [];
  for (const block of blocks) {
    if (block.type === "text" && mergedBlocks.length > 0 && mergedBlocks[mergedBlocks.length - 1].type === "text") {
      const prev = mergedBlocks[mergedBlocks.length - 1];
      const prevText = prev.html.replace(/<[^>]*>/g, "");
      const curText = block.html.replace(/<[^>]*>/g, "");
      if (prevText.length < 80 && curText.length < 80) {
        prev.html += " " + block.html;
        continue;
      }
    }
    if (block.type === "image") {
      if (mergedBlocks.find((b) => b.type === "image" && b.src === block.src)) continue;
    }
    if (block.type === "images") {
      block.srcs = block.srcs.filter((src) => !mergedBlocks.find((b) => b.type === "image" && b.src === src));
      if (block.srcs.length === 0) continue;
    }
    mergedBlocks.push(block);
  }

  return { blocks: mergedBlocks, shortUrls, pageTitle, pageUrl };
}

// ============================================================
// 第二步：替换占位符 + 图片转 base64 + 下载（注入页面运行）
// ============================================================
function finalizeAndDownload(data, resolvedMap) {
  const { blocks, shortUrls, pageTitle, pageUrl } = data;

  function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // 替换短链接占位符
  function replacePlaceholders(html) {
    for (const entry of shortUrls) {
      const resolved = resolvedMap[entry.id] || entry.shortUrl;
      const escaped = escapeHtml(resolved);
      html = html.split(entry.id).join(escaped);
    }
    return html;
  }

  blocks.forEach((b) => {
    if (b.html) b.html = replacePlaceholders(b.html);
    if (b.type === "list" && b.items) {
      b.items = b.items.map((item) => replacePlaceholders(item));
    }
  });

  // 图片转 base64
  function convertToBase64(src) {
    return new Promise((resolve) => {
      if (!src || src.startsWith("data:")) { resolve(src); return; }
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        try {
          const c = document.createElement("canvas");
          c.width = img.naturalWidth;
          c.height = img.naturalHeight;
          c.getContext("2d").drawImage(img, 0, 0);
          resolve(c.toDataURL("image/jpeg", 0.92));
        } catch (e) {
          resolve(src);
        }
      };
      img.onerror = () => resolve(src);
      img.src = src;
    });
  }

  const allImageUrls = [];
  blocks.forEach((b) => {
    if (b.type === "image") allImageUrls.push(b.src);
    if (b.type === "images") b.srcs.forEach((s) => allImageUrls.push(s));
  });
  const uniqueUrls = [...new Set(allImageUrls)];

  Promise.all(uniqueUrls.map((url) => convertToBase64(url).then((b64) => ({ url, b64 })))).then((results) => {
    const urlMap = {};
    results.forEach((r) => { urlMap[r.url] = r.b64; });

    blocks.forEach((b) => {
      if (b.type === "image" && urlMap[b.src]) b.src = urlMap[b.src];
      if (b.type === "images") b.srcs = b.srcs.map((s) => urlMap[s] || s);
    });

    const contentHtml = blocks.map((b) => blockToHtml(b)).join("\n");

    const now = new Date();
    const dateStr = [
      now.getFullYear(),
      String(now.getMonth() + 1).padStart(2, "0"),
      String(now.getDate()).padStart(2, "0")
    ].join("-") + " " + [
      String(now.getHours()).padStart(2, "0"),
      String(now.getMinutes()).padStart(2, "0")
    ].join(":");

    const finalHtml = buildFinalHtml(pageTitle, pageUrl, dateStr, contentHtml);

    const safeName = pageTitle.replace(/[<>:"/\\|?*]/g, "").replace(/\s+/g, "_").substring(0, 50);
    const blob = new Blob([finalHtml], { type: "text/html;charset=utf-8" });
    const dlUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = dlUrl;
    a.download = safeName + ".html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(dlUrl);
  });

  function blockToHtml(block) {
    switch (block.type) {
      case "heading":
        return `<h${block.level} class="cb-heading">${block.html}</h${block.level}>`;
      case "text":
        return `<p class="cb-text">${block.html}</p>`;
      case "image":
        return `<figure class="cb-figure"><img src="${block.src}" alt="${escapeHtml(block.alt || "")}" loading="lazy"></figure>`;
      case "images":
        return block.srcs.map((s) => `<figure class="cb-figure"><img src="${s}" alt="" loading="lazy"></figure>`).join("\n");
      case "code":
        return `<pre class="cb-code"><code>${escapeHtml(block.text)}</code></pre>`;
      case "blockquote":
        return `<blockquote class="cb-quote">${block.html}</blockquote>`;
      case "list": {
        const tag = block.ordered ? "ol" : "ul";
        const lis = block.items.map((item) => `<li>${item}</li>`).join("\n");
        return `<${tag} class="cb-list">\n${lis}\n</${tag}>`;
      }
      case "link":
        return `<p class="cb-link"><a href="${block.href}" target="_blank">${escapeHtml(block.text)}</a></p>`;
      case "hr":
        return `<hr class="cb-hr">`;
      case "video":
        return `<div class="cb-video"><video controls src="${block.src}" ${block.poster ? `poster="${block.poster}"` : ""}></video></div>`;
      case "table":
        return `<div class="cb-table">${block.html}</div>`;
      default:
        return "";
    }
  }

  function buildFinalHtml(title, url, dateStr, content) {
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} - 摘录</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.75;
  color: #1a1a1a;
  background: #fafafa;
  -webkit-font-smoothing: antialiased;
}
.cb-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  background: #fff;
  min-height: 100vh;
}
@media (max-width: 768px) {
  .cb-page { padding: 24px 16px 60px; }
}
.cb-source {
  background: #f7f8fa;
  border-left: 3px solid #4285f4;
  padding: 12px 16px;
  margin-bottom: 28px;
  border-radius: 0 6px 6px 0;
  font-size: 13px;
  color: #888;
}
.cb-source a { color: #4285f4; text-decoration: none; }
.cb-source a:hover { text-decoration: underline; }
.cb-source .cb-date { margin-top: 4px; }
.cb-heading {
  margin-top: 28px;
  margin-bottom: 12px;
  font-weight: 700;
  line-height: 1.4;
  color: #111;
}
h1.cb-heading { font-size: 26px; }
h2.cb-heading { font-size: 22px; }
h3.cb-heading { font-size: 19px; }
h4.cb-heading, h5.cb-heading, h6.cb-heading { font-size: 17px; }
.cb-text {
  margin-bottom: 14px;
  word-break: break-word;
}
.cb-text a { color: #4285f4; text-decoration: none; border-bottom: 1px solid rgba(66,133,244,0.3); }
.cb-text a:hover { border-bottom-color: #4285f4; }
.cb-text code {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
  font-family: "SF Mono", "Fira Code", "Consolas", monospace;
}
.cb-figure {
  margin: 16px 0;
  text-align: center;
}
.cb-figure img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  display: block;
  margin: 0 auto;
}
.cb-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 14px;
  line-height: 1.6;
  font-family: "SF Mono", "Fira Code", "Consolas", monospace;
  margin: 16px 0;
}
.cb-code code { background: none; padding: 0; color: inherit; font-size: inherit; }
.cb-quote {
  border-left: 3px solid #ddd;
  padding: 8px 16px;
  margin: 16px 0;
  color: #555;
  background: #fafafa;
  border-radius: 0 6px 6px 0;
}
.cb-list {
  margin: 14px 0;
  padding-left: 24px;
}
.cb-list li { margin-bottom: 6px; }
.cb-link { margin: 10px 0; }
.cb-link a {
  color: #4285f4;
  text-decoration: none;
  word-break: break-all;
}
.cb-link a:hover { text-decoration: underline; }
.cb-hr {
  border: none;
  border-top: 1px solid #e8e8e8;
  margin: 24px 0;
}
.cb-video { margin: 16px 0; }
.cb-video video { max-width: 100%; border-radius: 8px; }
.cb-table { margin: 16px 0; overflow-x: auto; }
.cb-table table { border-collapse: collapse; width: 100%; font-size: 14px; }
.cb-table th, .cb-table td { border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left; }
.cb-table th { background: #f5f5f5; font-weight: 600; }
.cb-table tr:nth-child(even) { background: #fafafa; }
@media print {
  body { background: #fff; }
  .cb-page { padding: 0; max-width: 100%; }
}
</style>
</head>
<body>
<div class="cb-page">
  <div class="cb-source">
    <div>来源：<a href="${url}" target="_blank">${title}</a></div>
    <div class="cb-date">保存时间：${dateStr}</div>
  </div>
  ${content}
</div>
</body>
</html>`;
  }
}
