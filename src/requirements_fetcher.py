import requests
from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict, Any

def fetch_job_requirements(url: str) -> Dict[str, Any]:
    """
    指定されたURLから人材要件を取得する。
    Webスクレイピングが失敗した場合は、PDFから抽出した固定の要件を返すフォールバック機能を持つ。

    Args:
        url: 人材要件が記載されたURL

    Returns:
        人材要件の辞書
    """
    logger.info(f"人材要件の取得を開始: {url}")
    try:
        # Webページから直接取得を試みる
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        soup = BeautifulSoup(response.text, 'html.parser')
        
        requirements = parse_requirements(soup)
        
        # 必須スキルが取得できているか簡易チェック
        if not requirements.get("skills"):
            raise ValueError("必須スキルの取得に失敗しました。HTMLの構造が変更された可能性があります。")
            
        logger.success("Webページから人材要件を正しく取得しました")
        return requirements

    except Exception as e:
        logger.error(f"要件の取得中にエラーが発生しました: {e}")
        logger.warning("フォールバックとして、PDFの情報に基づいた固定の要件を使用します。")
        return get_fallback_requirements()

def parse_requirements(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    BeautifulSoupオブジェクトから、実際のherp.careersのHTML構造に合わせて人材要件を解析・抽出する。
    """
    
    # データを格納する辞書
    data = {"skills": [], "research_area": [], "experience": "", "education": ""}

    # '必須スキル'セクションの情報を抽出
    skills_h3 = soup.find('h3', string='必須スキル')
    if skills_h3:
        # h3タグの次の要素（div）の中のpタグからテキストをリストとして取得
        content_div = skills_h3.find_next_sibling('div')
        if content_div:
            # ・で区切られている項目をリスト化
            items = [p.text.strip() for p in content_div.find_all('p') if p.text.strip()]
            # 必須スキルを解析
            for item in items:
                if "学位" in item:
                    data["education"] = item
                elif "経験" in item:
                    data["experience"] = item
                else:
                    # その他の項目は一般的なスキルとして追加
                    data["skills"].append(item)
    
    # '職務内容'から研究分野や技術を抽出
    job_description_h3 = soup.find('h3', string='仕事概要')
    if job_description_h3:
        content_div = job_description_h3.find_next_sibling('div')
        if content_div:
            # 職務内容からキーワードを抽出してresearch_areaに追加
            text = content_div.get_text()
            keywords = ["LLM", "大規模言語モデル", "Mamba", "自立型エージェント", "Retrieval Augmented Language Model"]
            for keyword in keywords:
                if keyword in text and keyword not in data["research_area"]:
                    data["research_area"].append(keyword)

    return data

def get_fallback_requirements() -> Dict[str, Any]:
    """
    PJT12_有望人材のレコメンド.pdf の内容に基づいた、固定の人材要件を返す。
    """
    requirements = {
        "skills": [
            "Python", "LLM", "大規模言語モデル", "データ加工", "モデル学習", "評価", "クラウドサービス",
            "Mamba", "自立型エージェント", "Retrieval Augmented Language Model", "Toolken"
        ],
        "experience": "生成系の言語モデルに関する、データ加工、モデル学習、評価の一連のサイクルを実施した経験",
        "education": "修士以上の学位",
        "research_area": [
            "LLMのフルスクラッチ構築", "継続学習", "LLMの社会的リスク", "Bias", 
            "Halucination", "Watermark", "LLM Agent"
        ],
        "other": ["日本語でのコミュニケーション及び文章作成能力", "英語での文章読解能力"]
    }
    return requirements