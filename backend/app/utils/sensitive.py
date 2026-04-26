"""
简易敏感词过滤器
采用 DFA（确定性有限自动机）算法实现 O(n) 匹配。
可扩展：从文件 / 数据库加载敏感词表。
"""

from typing import List


class SensitiveFilter:
    """
    基于 DFA 的敏感词过滤器
    用法:
        sf = SensitiveFilter(["敏感词1", "敏感词2"])
        sf.filter("这是一段包含敏感词1的文字")  # 返回 "这是一段包含***的文字"
    """

    def __init__(self, words: List[str] | None = None):
        self._fail = {}       # 失败指针（AC 自动机保留字段，DFA 暂用简化版本）
        self._dict = {}       # DFA 字典树
        if words:
            for w in words:
                self.add_word(w)

    def add_word(self, word: str):
        """向过滤器中添加一个敏感词"""
        if not word:
            return
        node = self._dict
        for ch in word:
            node = node.setdefault(ch, {})
        node["__end__"] = True   # 标记词尾

    def _build_ac(self):
        """
        构建 AC 自动机的 fail 指针（预留）。
        当前 DFA 版本无需此步，仅作占位。
        """
        pass

    def filter(self, text: str, replace_char: str = "*") -> str:
        """
        过滤敏感词，将匹配到的内容替换为 replace_char。
        返回替换后的字符串。
        """
        result = list(text)
        length = len(text)
        i = 0

        while i < length:
            node = self._dict
            if text[i] not in node:
                i += 1
                continue
            j = i
            while j < length and text[j] in node:
                node = node[text[j]]
                if node.get("__end__"):
                    # 从 i 到 j 匹配到一个敏感词
                    for k in range(i, j + 1):
                        result[k] = replace_char
                    i = j + 1
                    break
                j += 1
            else:
                i += 1
        return "".join(result)

    def contains(self, text: str) -> bool:
        """检查文本是否包含敏感词"""
        return self.filter(text, replace_char="") != text


# ── 全局默认实例（内置一些示例敏感词） ───────────────────
default_filter = SensitiveFilter([
    "敏感词1", "敏感词2",  # 占位，实际部署时请替换为真实词表
])
