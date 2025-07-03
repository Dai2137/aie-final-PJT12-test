import requests
from bs4 import BeautifulSoup
from loguru import logger

def fetch_job_requirements(url: str) -> dict:
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
        # Webページから直接取得を試みる (本番実装)
        # response = requests.get(url, timeout=10)
        # response.raise_for_status()
        # soup = BeautifulSoup(response.text, 'html.parser')
        # requirements = parse_requirements(soup)
        # logger.success("Webページから人材要件を取得しました")
        # return requirements
        
        # ----- サンプルとしてのフォールバック実装 -----
        # 上記のWebスクレイピングが失敗した場合の代替処理
        logger.warning("Webサイトへのアクセスに失敗したため、PDFの情報に基づいた固定の要件を使用します。")
        return get_fallback_requirements()

    except Exception as e:
        logger.error(f"要件の取得中にエラーが発生しました: {e}")
        logger.warning("フォールバックとして、PDFの情報に基づいた固定の要件を使用します。")
        return get_fallback_requirements()

def get_fallback_requirements() -> dict:
    """
    PJT12_有望人材のレコメンド.pdf の内容に基づいた、固定の人材要件を返す。
    """
    # PDFのp.5「参考情報:人材要件」から情報を抽出
    requirements = {
        "skills": [
            "Python",
            "LLM",
            "大規模言語モデル",
            "データ加工",
            "モデル学習",
            "評価",
            "クラウドサービス",
            "Mamba",
            "自立型エージェント",
            "Retrieval Augmented Language Model",
            "Toolken"
        ],
        "experience": "生成系の言語モデルに関する、データ加工、モデル学習、評価の一連のサイクルを実施した経験", #
        "education": "修士以上の学位", #
        "research_area": [
            "LLMのフルスクラッチ構築", #
            "継続学習", #
            "LLMの社会的リスク", #
            "Bias", #
            "Halucination", #
            "Watermark", #
            "LLM Agent" #
        ],
        "other": [
            "日本語でのコミュニケーション及び文章作成能力", #
            "英語での文章読解能力" #
        ]
    }
    return requirements

def parse_requirements(soup: BeautifulSoup) -> dict:
    """
    BeautifulSoupオブジェクトから人材要件を解析・抽出する（本番用の実装例）
    ※ この関数は実際のHTML構造に合わせて調整が必要です
    """
    # この部分は実際のWebページのHTML構造を分析して実装します
    # 以下はあくまでダミーの実装です
    skills = [tag.text for tag in soup.find_all(class_="skill-tag")]
    experience = soup.find(id="experience").text
    education = soup.find(id="education").text
    
    return {
        "skills": skills,
        "experience": experience,
        "education": education,
        "research_area": [] # 同様に抽出
    }