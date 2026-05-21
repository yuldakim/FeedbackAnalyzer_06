# -*- coding: utf-8 -*-
from typing import List
from feedback import Feedback
from constants import CATEGORY_KEYWORDS

S_KEYWORDS = {
    "긍정": [
        "좋아요", "만족", "감사", "친절", "좋다", "좋았", "좋은", "우수",
        "빠르", "정확", "신속", "안전", "괜찮", "인상적", "추천", "기대 이상",
        "합리", "꼼꼼", "뛰어납니다", "만족스럽", "좋았습니다", "좋습니다",
        "만족합니다", "굿", "최고", "최고입니다", "감사합니다",
    ],
    "부정": [
        "나쁘", "불만", "실망", "최악", "별로", "불편", "불만족", "문제",
        "불량", "불량품", "환불", "교환", "불만족스럽", "실망스럽",
        "비싸", "불친절", "늦다",
    ],
    "중립": [
        "괜찮", "보통", "평범", "무난", "그냥", "전반적", "완료",
        "적당", "나쁘지 않", "특별", "없",
    ],
}


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(kw in text for kw in keywords)


def filter_feedbacks(
    data_list: List[Feedback],
    sentiment_filter: str,
    keyword_filter: str,
) -> List[Feedback]:
    # Sentiment filtering
    if sentiment_filter != "전체":
        tmp_filtered = []
        for item in data_list:
            txt = item.text
            if _contains_any(txt, S_KEYWORDS["긍정"]):
                current_sentiment = "긍정"
            elif _contains_any(txt, S_KEYWORDS["부정"]):
                current_sentiment = "부정"
            elif _contains_any(txt, S_KEYWORDS["중립"]):
                current_sentiment = "중립"
            else:
                current_sentiment = "중립"

            if current_sentiment == sentiment_filter:
                tmp_filtered.append(item)
    else:
        tmp_filtered = list(data_list)

    # Keyword (category) filtering
    if keyword_filter != "전체":
        final_filtered = []
        if keyword_filter in CATEGORY_KEYWORDS:
            cat_map = CATEGORY_KEYWORDS[keyword_filter]
            for item in tmp_filtered:
                txt = item.text
                for sub_key, sub_keywords in cat_map.items():
                    if sub_key == "main":
                        continue
                    if _contains_any(txt, sub_keywords):
                        final_filtered.append(item)
                        break
    else:
        final_filtered = tmp_filtered

    for fb in final_filtered:
        print(fb.text)

    return final_filtered
