import requests
from bs4 import BeautifulSoup
from loguru import logger
from typing import Dict, Any, List

def fetch_job_requirements(url: str) -> Dict[str, Any]:
    """
    指定されたURLから静的HTMLを取得し、人材要件を抽出する。
    失敗した場合はフォールバックを返す。

    Args:
        url: 人材要件が記載されたURL

    Returns:
        人材要件の辞書
    """
    logger.info(f"人材要件の取得を開始: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        requirements = parse_requirements(soup)
        
        if not requirements.get("experience"):
            raise ValueError("必須経験の取得に失敗しました。HTMLの構造が変更された可能性があります。")
            
        logger.success("Webページから人材要件を正しく取得しました")
        return requirements

    except Exception as e:
        logger.error(f"要件の取得中にエラーが発生しました: {e}")
        logger.warning("フォールバックとして、PDFの情報に基づいた固定の要件を使用します。")
        return get_fallback_requirements()

def parse_requirements(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    herp.careersのHTML構造に合わせて人材要件を解析する。
    """
    data: Dict[str, Any] = {"skills": [], "research_area": [], "experience": "", "education": "", "other": []}

    # "with-heading"クラスを持つ全てのセクションを検索
    sections = soup.find_all('div', class_='with-heading')

    for section in sections:
        heading_tag = section.find('h2', class_='with-heading__heading')
        if not heading_tag:
            continue
        
        section_title = heading_tag.get_text(strip=True)
        content_div = section.find('div', class_='with-heading__content')
        if not content_div:
            continue
        
        # div内のテキストを改行で分割してリスト化
        items = [line.strip() for line in content_div.get_text(separator='\n').split('\n') if line.strip()]

        if section_title == '必須スキル':
            for item in items:
                item = item.lstrip('・') # 先頭の「・」を削除
                if '学位' in item:
                    data['education'] = item
                elif '経験' in item:
                    data['experience'] = item
                elif '能力' in item:
                    data['other'].append(item)
                else:
                    data['skills'].append(item)
        
        elif section_title == '歓迎スキル':
            # 歓迎スキルも 'skills' に追加
            for item in items:
                item = item.lstrip('・')
                data['skills'].append(item)
        
        elif section_title == '仕事概要':
            # 仕事概要から研究分野キーワードを抽出
            text = content_div.get_text()
            keywords = ["LLM", "Mamba", "自立型エージェント", "Retrieval Augmented Language Model", "Toolken", "Cameleon"]
            for keyword in keywords:
                if keyword in text and keyword not in data["research_area"]:
                    data["research_area"].append(keyword)

    return data


def get_fallback_requirements() -> Dict[str, Any]:
    """
    PJT12_有望人材のレコメンド.pdf の内容に基づいた、固定の人材要件を返す。
    """
    requirements = {
        "skills": ["Python", "LLM", "大規模言語モデル", "データ加工", "モデル学習", "評価", "クラウドサービス", "Mamba", "自立型エージェント", "Retrieval Augmented Language Model", "Toolken"],
        "experience": "生成系の言語モデルに関する、データ加工、モデル学習、評価の一連のサイクルを実施した経験",
        "education": "修士以上の学位",
        "research_area": ["LLMのフルスクラッチ構築", "継続学習", "LLMの社会的リスク", "Bias", "Halucination", "Watermark", "LLM Agent"],
        "other": ["日本語でのコミュニケーション及び文章作成能力", "英語での文章読解能力"]
    }
    return requirements


# Webページからテキストを取得するためのヘルパー関数
def fetch_text_from_url(url: str) -> str:
    try:
        # 一般的なブラウザからのアクセスを装うためのヘッダーを追加
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # ヘッダーを付けてリクエストを送信
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_divs = soup.find_all('div', class_='multiline-text')
        full_text = ' '.join(div.get_text(separator=' ', strip=True) for div in content_divs)
        
        return full_text
        
    except Exception as e:
        logger.error(f"URLからのテキスト取得エラー: {e}")
        return ""
