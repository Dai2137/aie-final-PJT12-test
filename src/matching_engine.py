"""人材マッチングエンジン"""

from typing import Dict, List, Tuple
from loguru import logger
import re
from dataclasses import dataclass


@dataclass
class MatchResult:
    """マッチング結果"""
    candidate_name: str
    match_score: int
    potential_score: int
    summary: str
    strengths: List[str]
    concerns: List[str]
    reference_links: List[str]
    source: str
    metadata: Dict


class MatchingEngine:
    """人材マッチングエンジン"""
    
    def __init__(self):
        """初期化"""
        logger.info("マッチングエンジンを初期化しました")
    
    def calculate_basic_match_score(self, candidate: Dict, requirements: Dict) -> int:
        """
        基本的なマッチスコアを計算
        
        Args:
            candidate: 候補者情報
            requirements: 人材要件
            
        Returns:
            マッチスコア (0-100)
        """
        score = 0
        max_score = 0
        
        profile_text = candidate.get("profile_text", "").lower()
        
        # スキルマッチング (40点満点)
        required_skills = requirements.get("skills", [])
        if required_skills:
            skill_matches = 0
            for skill in required_skills:
                if skill.lower() in profile_text:
                    skill_matches += 1
            
            skill_score = min(40, (skill_matches / len(required_skills)) * 40)
            score += skill_score
        max_score += 40
        
        # 経験年数マッチング (20点満点)
        experience_req = requirements.get("experience", "")
        if experience_req:
            exp_score = self._calculate_experience_score(profile_text, experience_req)
            score += exp_score
        max_score += 20
        
        # 教育背景マッチング (20点満点)
        education_req = requirements.get("education", "")
        if education_req:
            edu_score = self._calculate_education_score(profile_text, education_req)
            score += edu_score
        max_score += 20
        
        # 研究分野マッチング (20点満点)
        research_areas = requirements.get("research_area", [])
        if research_areas:
            research_matches = 0
            for area in research_areas:
                if area.lower() in profile_text:
                    research_matches += 1
            
            research_score = min(20, (research_matches / len(research_areas)) * 20)
            score += research_score
        max_score += 20
        
        # 正規化してパーセンテージに変換
        if max_score > 0:
            final_score = int((score / max_score) * 100)
        else:
            final_score = 50  # デフォルト値
        
        return max(0, min(100, final_score))
    
    def _calculate_experience_score(self, profile_text: str, experience_req: str) -> int:
        """経験年数スコアを計算"""
        # 経験年数の抽出を試行
        exp_numbers = re.findall(r'(\d+)年', profile_text)
        
        if not exp_numbers:
            return 10  # 不明な場合は中間値
        
        max_exp = max(int(num) for num in exp_numbers)
        
        # 要件から必要年数を抽出
        req_numbers = re.findall(r'(\d+)', experience_req)
        if req_numbers:
            required_years = int(req_numbers[0])
            if max_exp >= required_years:
                return 20
            elif max_exp >= required_years * 0.7:
                return 15
            else:
                return 10
        
        return 10
    
    def _calculate_education_score(self, profile_text: str, education_req: str) -> int:
        """教育背景スコアを計算"""
        education_keywords = {
            "博士": 20,
            "PhD": 20,
            "修士": 15,
            "Master": 15,
            "学士": 10,
            "Bachelor": 10,
            "大学院": 15,
            "大学": 10
        }
        
        max_education_score = 0
        for keyword, score in education_keywords.items():
            if keyword.lower() in profile_text:
                max_education_score = max(max_education_score, score)
        
        # 要件との比較
        if "博士" in education_req.lower() or "phd" in education_req.lower():
            if max_education_score >= 20:
                return 20
            elif max_education_score >= 15:
                return 15
            else:
                return 5
        elif "修士" in education_req.lower() or "master" in education_req.lower():
            if max_education_score >= 15:
                return 20
            elif max_education_score >= 10:
                return 15
            else:
                return 10
        
        return max_education_score
    
    def calculate_potential_score(self, candidate: Dict, gemini_analysis: Dict) -> int:
        """
        ポテンシャルスコアを計算
        
        Args:
            candidate: 候補者情報
            gemini_analysis: Gemini分析結果
            
        Returns:
            ポテンシャルスコア (0-100)
        """
        # Gemini分析結果を優先
        if "potential_score" in gemini_analysis:
            return gemini_analysis["potential_score"]
        
        # フォールバック計算
        score = 50  # ベーススコア
        
        metadata = candidate.get("metadata", {})
        
        # 論文数・被引用数（研究者の場合）
        if "publications" in metadata:
            publications = metadata["publications"]
            if publications > 20:
                score += 20
            elif publications > 10:
                score += 15
            elif publications > 5:
                score += 10
        
        if "citations" in metadata:
            citations = metadata["citations"]
            if citations > 300:
                score += 15
            elif citations > 100:
                score += 10
            elif citations > 50:
                score += 5
        
        # GitHubリポジトリ数（エンジニアの場合）
        if "public_repos" in metadata:
            repos = metadata["public_repos"]
            if repos > 50:
                score += 15
            elif repos > 20:
                score += 10
            elif repos > 10:
                score += 5
        
        # 経験年数ボーナス
        if "experience_years" in metadata:
            exp_years = metadata["experience_years"]
            if exp_years > 7:
                score += 10
            elif exp_years > 4:
                score += 5
        
        return max(0, min(100, score))
    
    def rank_candidates(self, match_results: List[MatchResult]) -> List[MatchResult]:
        """
        候補者をランキング
        
        Args:
            match_results: マッチング結果リスト
            
        Returns:
            ランキング済みマッチング結果リスト
        """
        def calculate_combined_score(result: MatchResult) -> float:
            # マッチスコア70%、ポテンシャルスコア30%の重み付け
            return result.match_score * 0.7 + result.potential_score * 0.3
        
        ranked_results = sorted(
            match_results,
            key=calculate_combined_score,
            reverse=True
        )
        
        logger.info(f"候補者ランキング完了: {len(ranked_results)}名")
        return ranked_results
    
    def filter_candidates(self, match_results: List[MatchResult], 
                         min_match_score: int = 30, 
                         max_results: int = 10) -> List[MatchResult]:
        """
        候補者をフィルタリング
        
        Args:
            match_results: マッチング結果リスト
            min_match_score: 最小マッチスコア
            max_results: 最大結果数
            
        Returns:
            フィルタリング済み結果リスト
        """
        filtered_results = [
            result for result in match_results 
            if result.match_score >= min_match_score
        ]
        
        final_results = filtered_results[:max_results]
        
        logger.info(f"候補者フィルタリング完了: {len(final_results)}名 (最小スコア: {min_match_score})")
        return final_results