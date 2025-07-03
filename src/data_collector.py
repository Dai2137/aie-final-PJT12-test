import os
import requests
from typing import Dict, List
from loguru import logger
import time
import random

class DataCollector:
    """人材データ収集クラス (GitHub API対応版)"""

    # __init__がgithub_patを引数で受け取るように変更
    def __init__(self, github_pat: str):
        self.session = requests.Session()
        # 引数で受け取ったキーを直接使う
        if not github_pat:
            logger.warning("GITHUB_PATが設定されていません。...")
        else:
            logger.info("GITHUB_PATを読み込みました。...")
            self.session.headers.update({
                'Authorization': f'token {github_pat}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'TalentRecommender-Project'
            })
        logger.info("データ収集モジュールを初期化しました")
    def search_github_profiles(self, query: str, max_results: int = 10) -> List[Dict]:
        """GitHub APIを使ってユーザーを検索し、詳細プロフィールを取得する"""
        logger.info(f"GitHubユーザー検索開始: {query}")
        search_url = "https://api.github.com/search/users"
        params = {'q': query, 'per_page': max_results}
        
        try:
            search_response = self.session.get(search_url, params=params)
            search_response.raise_for_status()  # HTTPエラーがあれば例外を発生
            users = search_response.json().get('items', [])
            
            candidates = []
            for user_item in users:
                time.sleep(random.uniform(0.5, 1.0)) # APIへの負荷を考慮
                
                # 詳細なプロフィールを取得
                profile_url = user_item['url']
                profile_response = self.session.get(profile_url)
                if profile_response.status_code != 200:
                    continue
                profile_data = profile_response.json()
                
                # 候補者情報を整形
                candidate = {
                    "source": "GitHub",
                    "name": profile_data.get('name') or profile_data.get('login'),
                    "profile_text": f"Bio: {profile_data.get('bio', 'N/A')}. Location: {profile_data.get('location', 'N/A')}. Company: {profile_data.get('company', 'N/A')}. Followers: {profile_data.get('followers', 0)}.",
                    "reference_links": [profile_data.get('html_url')],
                    "metadata": {
                        "public_repos": profile_data.get('public_repos', 0),
                        "followers": profile_data.get('followers', 0),
                        "location": profile_data.get('location', 'N/A')
                    }
                }
                candidates.append(candidate)
            
            logger.info(f"GitHubユーザー検索完了: {len(candidates)}件")
            return candidates

        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub APIリクエストエラー: {e}")
            return []

    def search_researchmap(self, keywords: List[str]) -> List[Dict]:
        """ResearchMapから研究者情報を検索（モックデータ）"""
        logger.info(f"ResearchMap検索開始: {keywords}")
        mock_data = [
            { "name": "研究者A", "affiliation": "東京大学", "research_areas": ["機械学習", "深層学習"], "description": "深層学習を用いた自然言語処理の研究に従事。", "profile_url": "https://researchmap.jp/example1"},
            { "name": "研究者B", "affiliation": "京都大学", "research_areas": ["コンピュータビジョン", "深層学習"], "description": "医療画像解析への深層学習応用で注目される。", "profile_url": "https://researchmap.jp/example2"}
        ]
        filtered_data = [r for r in mock_data if any(k in ' '.join(r['research_areas']) for k in keywords)]
        logger.info(f"ResearchMap検索完了: {len(filtered_data)}件")
        return filtered_data

    def collect_candidate_data(self, search_params: Dict) -> List[Dict]:
        """複数のソースから候補者データを収集"""
        logger.info("候補者データ収集開始")
        all_candidates = []
        
        # ResearchMapから検索 (モック)
        if "research_keywords" in search_params:
            research_data = self.search_researchmap(search_params["research_keywords"])
            for data in research_data:
                all_candidates.append({
                    "source": "ResearchMap", "name": data["name"],
                    "profile_text": f"{data['description']} 所属: {data['affiliation']}. 研究分野: {', '.join(data['research_areas'])}.",
                    "reference_links": [data["profile_url"]], "metadata": data
                })
        
        # GitHubから検索 (本物)
        if "job_keywords" in search_params:
            keywords = search_params.get("job_keywords", [])
            # 'python'を除いた重要キーワードをいくつか選ぶ
            core_keywords = [kw for kw in keywords if kw.lower() != 'python'][:4]

            # 重複を防ぐため、候補者を一時的に保存する辞書
            github_candidates_dict = {}

            # 主要なキーワードそれぞれで検索を実行
            for keyword in core_documents:
                query_str = f"language:python {keyword} location:japan"
                # 1回の検索あたりの取得数を減らし、幅広く探す
                results = self.search_github_profiles(query_str, max_results=3) 
                for candidate in results:
                    # ユーザーURLをキーにして重複を排除
                    candidate_url = candidate["reference_links"][0]
                    if candidate_url not in github_candidates_dict:
                        github_candidates_dict[candidate_url] = candidate

                # APIへの連続アクセスを避けるための短い待機
                time.sleep(1)

            # 辞書からリストに変換して最終的な候補者リストに追加
            all_candidates.extend(list(github_candidates_dict.values()))
        
        logger.info(f"候補者データ収集完了: {len(all_candidates)}件")
        return all_candidates