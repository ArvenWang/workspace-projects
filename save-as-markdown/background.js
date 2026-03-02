// 创建右键菜单
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "save-as-markdown",
    title: "保存选中文本为 Markdown",
    contexts: ["selection"]
  });
});

// 处理右键菜单点击
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "save-as-markdown") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: getSelectionAndDownload,
      args: [tab.title, tab.url]
    });
  }
});

// 注入到页面中执行的函数
function getSelectionAndDownload(pageTitle, pageUrl) {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return;

  // 获取选中区域的 HTML 内容
  const range = selection.getRangeAt(0);
  const container = document.createElement("div");
  container.appendChild(range.cloneContents());
  const html = container.innerHTML;

  // 将 HTML 转换为 Markdown
  function htmlToMarkdown(html) {
    const temp = document.createElement("div");
    temp.innerHTML = html;
    return nodeToMarkdown(temp).trim();
  }

  function nodeToMarkdown(node) {
    let result = "";

    for (const child of node.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) {
        result += child.textContent;
        continue;
      }

      if (child.nodeType !== Node.ELEMENT_NODE) continue;

      const tag = child.tagName.toLowerCase();

      switch (tag) {
        case "h1":
          result += "\n# " + nodeToMarkdown(child) + "\n\n";
          break;
        case "h2":
          result += "\n## " + nodeToMarkdown(child) + "\n\n";
          break;
        case "h3":
          result += "\n### " + nodeToMarkdown(child) + "\n\n";
          break;
        case "h4":
          result += "\n#### " + nodeToMarkdown(child) + "\n\n";
          break;
        case "h5":
          result += "\n##### " + nodeToMarkdown(child) + "\n\n";
          break;
        case "h6":
          result += "\n###### " + nodeToMarkdown(child) + "\n\n";
          break;
        case "p":
          result += "\n" + nodeToMarkdown(child) + "\n\n";
          break;
        case "br":
          result += "\n";
          break;
        case "strong":
        case "b":
          result += "**" + nodeToMarkdown(child) + "**";
          break;
        case "em":
        case "i":
          result += "*" + nodeToMarkdown(child) + "*";
          break;
        case "del":
        case "s":
          result += "~~" + nodeToMarkdown(child) + "~~";
          break;
        case "code":
          if (child.parentElement && child.parentElement.tagName.toLowerCase() === "pre") {
            result += nodeToMarkdown(child);
          } else {
            result += "`" + child.textContent + "`";
          }
          break;
        case "pre": {
          const codeEl = child.querySelector("code");
          const codeText = codeEl ? codeEl.textContent : child.textContent;
          const langClass = (codeEl && codeEl.className) || "";
          const langMatch = langClass.match(/language-(\w+)/);
          const lang = langMatch ? langMatch[1] : "";
          result += "\n```" + lang + "\n" + codeText + "\n```\n\n";
          break;
        }
        case "a": {
          const href = child.getAttribute("href") || "";
          const text = nodeToMarkdown(child);
          result += "[" + text + "](" + href + ")";
          break;
        }
        case "img": {
          const src = child.getAttribute("src") || "";
          const alt = child.getAttribute("alt") || "image";
          result += "![" + alt + "](" + src + ")";
          break;
        }
        case "ul":
          result += "\n" + listToMarkdown(child, "-", 0) + "\n";
          break;
        case "ol":
          result += "\n" + listToMarkdown(child, "1.", 0) + "\n";
          break;
        case "li":
          result += nodeToMarkdown(child);
          break;
        case "blockquote":
          result += "\n" + nodeToMarkdown(child).split("\n").map(line => "> " + line).join("\n") + "\n\n";
          break;
        case "hr":
          result += "\n---\n\n";
          break;
        case "table":
          result += "\n" + tableToMarkdown(child) + "\n\n";
          break;
        case "div":
        case "section":
        case "article":
        case "main":
        case "span":
          result += nodeToMarkdown(child);
          break;
        default:
          result += nodeToMarkdown(child);
          break;
      }
    }

    return result;
  }

  function listToMarkdown(listNode, marker, indent) {
    let result = "";
    let index = 1;
    for (const li of listNode.children) {
      if (li.tagName.toLowerCase() !== "li") continue;
      const prefix = " ".repeat(indent) + (marker === "1." ? index + ". " : "- ");
      let content = "";

      for (const child of li.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) {
          content += child.textContent.trim();
        } else if (child.nodeType === Node.ELEMENT_NODE) {
          const tag = child.tagName.toLowerCase();
          if (tag === "ul") {
            content += "\n" + listToMarkdown(child, "-", indent + 2);
          } else if (tag === "ol") {
            content += "\n" + listToMarkdown(child, "1.", indent + 2);
          } else {
            content += nodeToMarkdown(child);
          }
        }
      }

      result += prefix + content.trim() + "\n";
      index++;
    }
    return result;
  }

  function tableToMarkdown(tableNode) {
    const rows = tableNode.querySelectorAll("tr");
    if (rows.length === 0) return "";

    const matrix = [];
    for (const row of rows) {
      const cells = row.querySelectorAll("th, td");
      const rowData = [];
      for (const cell of cells) {
        rowData.push(cell.textContent.trim().replace(/\|/g, "\\|"));
      }
      matrix.push(rowData);
    }

    if (matrix.length === 0) return "";

    const colCount = Math.max(...matrix.map(r => r.length));
    const lines = [];

    // Header
    const header = matrix[0];
    while (header.length < colCount) header.push("");
    lines.push("| " + header.join(" | ") + " |");
    lines.push("| " + header.map(() => "---").join(" | ") + " |");

    // Body
    for (let i = 1; i < matrix.length; i++) {
      const row = matrix[i];
      while (row.length < colCount) row.push("");
      lines.push("| " + row.join(" | ") + " |");
    }

    return lines.join("\n");
  }

  // 转换
  const markdown = htmlToMarkdown(html);

  // 构建最终内容，包含来源信息
  const now = new Date();
  const dateStr = now.getFullYear() + "-" +
    String(now.getMonth() + 1).padStart(2, "0") + "-" +
    String(now.getDate()).padStart(2, "0") + " " +
    String(now.getHours()).padStart(2, "0") + ":" +
    String(now.getMinutes()).padStart(2, "0");

  const content = `> 来源: [${pageTitle}](${pageUrl})\n> 时间: ${dateStr}\n\n---\n\n${markdown}`;

  // 生成文件名
  const safeName = pageTitle
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 50);
  const fileName = safeName + ".md";

  // 下载文件
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
