"""有望人材レコメンドシステム メインクラス"""

import os
from typing import Dict, List, Optional
from loguru import logger
from dotenv import load_dotenv

from .gemini_client import GeminiClient
from .data_collector import DataCollector
from .matching_engine import MatchingEngine, MatchResult

load_dotenv()


class TalentRecommender:
    """有望人材レコメンドシステム"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            gemini_api_key: Gemini API キー（環境変数から取得される場合はNone）
        """
        logger.info("TalentRecommenderシステムを初期化中...")
        
        self.gemini_client = GeminiClient(gemini_api_key)
        self.data_collector = DataCollector()
        self.matching_engine = MatchingEngine()
        
        # 設定値
        self.max_candidates = int(os.getenv("MAX_CANDIDATES", "10"))
        
        logger.info("TalentRecommenderシステムの初期化完了")
    
    def find_candidates(self, requirements: Dict) -> List[MatchResult]:
        """
        人材要件に基づいて候補者を検索・分析
        
        Args:
            requirements: 人材要件辞書
                例: {
                    "skills": ["機械学習", "Python", "データ分析"],
                    "experience": "3年以上", 
                    "education": "修士以上",
                    "research_area": ["深層学習", "自然言語処理"]
                }
        
        Returns:
            マッチング結果リスト（ランキング済み）
        """
        logger.info("候補者検索開始")
        logger.info(f"検索要件: {requirements}")
        
        try:
            # 1. データ収集
            search_params = self._convert_requirements_to_search_params(requirements)
            candidates = self.data_collector.collect_candidate_data(search_params)
            
            if not candidates:
                logger.warning("候補者データが見つかりませんでした")
                return []
            
            # 2. 各候補者を分析・評価
            match_results = []
            for candidate in candidates:
                try:
                    result = self._analyze_candidate(candidate, requirements)
                    if result:
                        match_results.append(result)
                except Exception as e:
                    logger.error(f"候補者分析エラー ({candidate.get('name', 'Unknown')}): {e}")
                    continue
            
            # 3. ランキング
            ranked_results = self.matching_engine.rank_candidates(match_results)
            
            # 4. フィルタリング
            final_results = self.matching_engine.filter_candidates(
                ranked_results, 
                min_match_score=30,
                max_results=self.max_candidates
            )
            
            logger.info(f"候補者検索完了: {len(final_results)}名の候補者を発見")
            return final_results
            
        except Exception as e:
            logger.error(f"候補者検索エラー: {e}")
            return []
    
    def _convert_requirements_to_search_params(self, requirements: Dict) -> Dict:
        """
        人材要件を検索パラメータに変換
        
        Args:
            requirements: 人材要件
            
        Returns:
            検索パラメータ
        """
        search_params = {}
        
        # スキルと研究分野を統合
        all_keywords = []
        all_keywords.extend(requirements.get("skills", []))
        all_keywords.extend(requirements.get("research_area", []))
        
        if all_keywords:
            search_params["research_keywords"] = all_keywords
            search_params["job_keywords"] = all_keywords
        
        return search_params
    
    def _analyze_candidate(self, candidate: Dict, requirements: Dict) -> Optional[MatchResult]:
        """
        候補者を分析してマッチング結果を生成
        
        Args:
            candidate: 候補者データ
            requirements: 人材要件
            
        Returns:
            マッチング結果 or None
        """
        try:
            # 基本的なマッチスコア計算
            basic_match_score = self.matching_engine.calculate_basic_match_score(
                candidate, requirements
            )
            
            # Gemini APIによる詳細分析
            gemini_analysis = self.gemini_client.analyze_profile(
                candidate.get("profile_text", ""), 
                requirements
            )
            
            # Gemini分析結果を優先し、基本スコアをフォールバックとして使用
            final_match_score = gemini_analysis.get("match_score", basic_match_score)
            
            # ポテンシャルスコア計算
            potential_score = self.matching_engine.calculate_potential_score(
                candidate, gemini_analysis
            )
            
            # 結果作成
            match_result = MatchResult(
                candidate_name=candidate.get("name", "不明"),
                match_score=final_match_score,
                potential_score=potential_score,
                summary=gemini_analysis.get("summary", "分析結果なし"),
                strengths=gemini_analysis.get("strengths", []),
                concerns=gemini_analysis.get("concerns", []),
                reference_links=candidate.get("reference_links", []),
                source=candidate.get("source", "不明"),
                metadata=candidate.get("metadata", {})
            )
            
            logger.debug(f"候補者分析完了: {match_result.candidate_name} (マッチ度: {final_match_score})")
            return match_result
            
        except Exception as e:
            logger.error(f"候補者分析エラー: {e}")
            return None
    
    def generate_approach_strategies(self, match_results: List[MatchResult]) -> Dict[str, str]:
        """
        候補者へのアプローチ戦略を生成
        
        Args:
            match_results: マッチング結果リスト
            
        Returns:
            候補者名をキーとするアプローチ戦略辞書
        """
        strategies = {}
        
        for result in match_results:
            try:
                candidate_info = {
                    "name": result.candidate_name,
                    "match_score": result.match_score,
                    "potential_score": result.potential_score,
                    "summary": result.summary,
                    "strengths": result.strengths,
                    "concerns": result.concerns
                }
                
                strategy = self.gemini_client.generate_approach_strategy(candidate_info)
                strategies[result.candidate_name] = strategy
                
            except Exception as e:
                logger.error(f"アプローチ戦略生成エラー ({result.candidate_name}): {e}")
                strategies[result.candidate_name] = "個別相談により戦略を検討してください"
        
        return strategies
    
    def export_results_to_dict(self, match_results: List[MatchResult]) -> List[Dict]:
        """
        マッチング結果を辞書形式でエクスポート
        
        Args:
            match_results: マッチング結果リスト
            
        Returns:
            辞書形式の結果リスト
        """
        exported_results = []
        
        for result in match_results:
            exported_result = {
                "name": result.candidate_name,
                "match_score": result.match_score,
                "potential_score": result.potential_score,
                "summary": result.summary,
                "strengths": result.strengths,
                "concerns": result.concerns,
                "reference_links": result.reference_links,
                "source": result.source,
                "combined_score": result.match_score * 0.7 + result.potential_score * 0.3
            }
            exported_results.append(exported_result)
        
        return exported_results


def main():
    """メイン実行関数（テスト用）"""
    # ログ設定
    logger.add("talent_recommender.log", rotation="1 MB")
    
    # システム初期化
    recommender = TalentRecommender()
    
    # サンプル要件
    sample_requirements = {
        "skills": ["機械学習", "Python", "データ分析"],
        "experience": "3年以上",
        "education": "修士以上",
        "research_area": ["深層学習", "自然言語処理"]
    }
    
    # 候補者検索
    results = recommender.find_candidates(sample_requirements)
    
    # 結果表示
    print("\n=== 有望人材レコメンド結果 ===")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.candidate_name}")
        print(f"   マッチ度: {result.match_score}点")
        print(f"   有望度: {result.potential_score}点")
        print(f"   要約: {result.summary}")
        print(f"   強み: {', '.join(result.strengths)}")
        print(f"   参照: {', '.join(result.reference_links)}")
        print(f"   情報源: {result.source}")
    
    # アプローチ戦略生成
    if results:
        print("\n=== アプローチ戦略 ===")
        strategies = recommender.generate_approach_strategies(results[:3])  # 上位3名
        for name, strategy in strategies.items():
            print(f"\n【{name}】")
            print(strategy)


if __name__ == "__main__":
    main()