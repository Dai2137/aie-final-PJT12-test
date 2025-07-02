"""データ収集モジュール"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from loguru import logger
import time
import random


class DataCollector:
    """人材データ収集クラス"""
    
    def __init__(self):
        """初期化"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        logger.info("データ収集モジュールを初期化しました")

    def search_researchmap(self, keywords: List[str]) -> List[Dict]:
        """
        ResearchMapから研究者情報を検索（モックデータ）
        
        Args:
            keywords: 検索キーワードリスト
            
        Returns:
            研究者情報リスト
        """
        logger.info(f"ResearchMap検索開始: {keywords}")
        
        # 実際のAPIが利用できない場合はモックデータを返す
        mock_data = [
            {
                "name": "研究者A",
                "affiliation": "東京大学 大学院情報理工学研究科",
                "research_areas": ["機械学習", "深層学習", "自然言語処理"],
                "publications": 25,
                "citations": 320,
                "profile_url": "https://researchmap.jp/example1",
                "description": "深層学習を用いた自然言語処理の研究に従事。特にTransformerモデルの改良に関する研究で成果を上げている。"
            },
            {
                "name": "研究者B",
                "affiliation": "京都大学 情報学研究科",
                "research_areas": ["コンピュータビジョン", "画像認識", "深層学習"],
                "publications": 18,
                "citations": 180,
                "profile_url": "https://researchmap.jp/example2",
                "description": "コンピュータビジョンの分野で活躍。特に医療画像解析への深層学習応用で注目される。"
            },
            {
                "name": "研究者C",
                "affiliation": "慶應義塾大学 理工学部",
                "research_areas": ["データマイニング", "ビッグデータ", "機械学習"],
                "publications": 30,
                "citations": 450,
                "profile_url": "https://researchmap.jp/example3",
                "description": "大規模データ解析の専門家。産業界との連携も多く、実用的なAIシステム開発に貢献。"
            }
        ]
        
        # キーワードに基づくフィルタリング（簡易実装）
        filtered_data = []
        for researcher in mock_data:
            if any(keyword.lower() in ' '.join(researcher['research_areas']).lower() 
                  for keyword in keywords):
                filtered_data.append(researcher)
        
        logger.info(f"ResearchMap検索完了: {len(filtered_data)}件")
        return filtered_data

    def search_linkedin_profiles(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        LinkedIn風のプロフィール検索（モックデータ）
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数
            
        Returns:
            プロフィール情報リスト
        """
        logger.info(f"LinkedIn風検索開始: {query}")
        
        # 実際のLinkedIn APIは利用規約により制限があるため、モックデータを使用
        mock_profiles = [
            {
                "name": "エンジニアA",
                "title": "データサイエンティスト",
                "company": "株式会社AI研究所",
                "location": "東京",
                "experience_years": 5,
                "skills": ["Python", "機械学習", "SQL", "TensorFlow"],
                "education": "東京工業大学 情報工学科 修士",
                "profile_url": "https://linkedin.com/in/example1",
                "summary": "5年間のデータサイエンス経験。機械学習モデルの開発と運用に従事。"
            },
            {
                "name": "エンジニアB",
                "title": "AIエンジニア",
                "company": "テックベンチャー株式会社",
                "location": "大阪",
                "experience_years": 3,
                "skills": ["Python", "PyTorch", "自然言語処理", "クラウド"],
                "education": "大阪大学 基礎工学部 学士",
                "profile_url": "https://linkedin.com/in/example2",
                "summary": "スタートアップでAIプロダクト開発をリード。NLPアプリケーションが専門。"
            },
            {
                "name": "エンジニアC",
                "title": "機械学習エンジニア",
                "company": "大手IT企業",
                "location": "東京",
                "experience_years": 4,
                "skills": ["Python", "scikit-learn", "深層学習", "MLOps"],
                "education": "早稲田大学 理工学部 修士",
                "profile_url": "https://linkedin.com/in/example3",
                "summary": "大規模機械学習システムの設計・構築。MLOpsの導入により開発効率化を実現。"
            }
        ]
        
        # クエリに基づく簡易フィルタリング
        filtered_profiles = []
        query_lower = query.lower()
        
        for profile in mock_profiles:
            if (query_lower in profile['title'].lower() or 
                query_lower in ' '.join(profile['skills']).lower() or
                query_lower in profile['summary'].lower()):
                filtered_profiles.append(profile)
        
        result = filtered_profiles[:max_results]
        logger.info(f"LinkedIn風検索完了: {len(result)}件")
        return result

    def get_github_profile(self, username: str) -> Optional[Dict]:
        """
        GitHub プロフィール情報を取得
        
        Args:
            username: GitHub ユーザー名
            
        Returns:
            プロフィール情報 or None
        """
        try:
            url = f"https://api.github.com/users/{username}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                profile = {
                    "name": data.get("name", username),
                    "bio": data.get("bio", ""),
                    "location": data.get("location", ""),
                    "public_repos": data.get("public_repos", 0),
                    "followers": data.get("followers", 0),
                    "following": data.get("following", 0),
                    "created_at": data.get("created_at", ""),
                    "profile_url": data.get("html_url", ""),
                    "avatar_url": data.get("avatar_url", "")
                }
                logger.info(f"GitHub プロフィール取得成功: {username}")
                return profile
            
        except Exception as e:
            logger.error(f"GitHub プロフィール取得エラー: {e}")
        
        return None

    def collect_candidate_data(self, search_params: Dict) -> List[Dict]:
        """
        複数のソースから候補者データを収集
        
        Args:
            search_params: 検索パラメータ
            
        Returns:
            統合された候補者データリスト
        """
        logger.info("候補者データ収集開始")
        all_candidates = []
        
        # ResearchMapから検索
        if "research_keywords" in search_params:
            research_data = self.search_researchmap(
                search_params["research_keywords"]
            )
            for data in research_data:
                candidate = {
                    "source": "ResearchMap",
                    "name": data["name"],
                    "profile_text": f"{data['description']} 所属: {data['affiliation']} 研究分野: {', '.join(data['research_areas'])} 論文数: {data['publications']} 被引用数: {data['citations']}",
                    "reference_links": [data["profile_url"]],
                    "metadata": data
                }
                all_candidates.append(candidate)
        
        # LinkedIn風データから検索
        if "job_keywords" in search_params:
            linkedin_data = self.search_linkedin_profiles(
                " ".join(search_params["job_keywords"])
            )
            for data in linkedin_data:
                candidate = {
                    "source": "LinkedIn風",
                    "name": data["name"],
                    "profile_text": f"{data['summary']} 職種: {data['title']} 会社: {data['company']} 経験: {data['experience_years']}年 スキル: {', '.join(data['skills'])} 学歴: {data['education']}",
                    "reference_links": [data["profile_url"]],
                    "metadata": data
                }
                all_candidates.append(candidate)
        
        logger.info(f"候補者データ収集完了: {len(all_candidates)}件")
        return all_candidates

    def _add_delay(self):
        """API呼び出し間の遅延を追加"""
        time.sleep(random.uniform(0.5, 1.5))