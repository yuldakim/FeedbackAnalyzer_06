# -*- coding: utf-8 -*-
from typing import List, Dict
from feedback import Feedback
from constants import SENTIMENT_KEYWORDS, CATEGORY_KEYWORDS


class TextAnalyzer:
    global_sent: Dict[str, int] = {}
    global_kw: Dict[str, int] = {}

    @staticmethod
    def _contains_any(text: str, keywords: List[str]) -> bool:
        return any(kw in text for kw in keywords)

    def sent(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        res = {"긍정": 0, "중립": 0, "부정": 0}

        for f in feedbacks:
            txt = f.text
            if self._contains_any(txt, SENTIMENT_KEYWORDS["긍정"]):
                s = "긍정"
            elif self._contains_any(txt, SENTIMENT_KEYWORDS["부정"]):
                s = "부정"
            else:
                s = "중립"
            res[s] += 1

        TextAnalyzer.global_sent = res
        return res

    def kw(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        res = {cat: 0 for cat in CATEGORY_KEYWORDS}

        for f in feedbacks:
            txt = f.text
            for cat, sub_map in CATEGORY_KEYWORDS.items():
                if "main" in sub_map:
                    if self._contains_any(txt, sub_map["main"]):
                        res[cat] += 1

        TextAnalyzer.global_kw = res
        return res
