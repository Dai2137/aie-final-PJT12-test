#!/usr/bin/env python3
"""
有望人材レコメンドシステム実行例

使用前に .env ファイルを作成し、GEMINI_API_KEY を設定してください。
"""

import sys
import os

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from talent_recommender import TalentRecommender
from loguru import logger


def main():
    """メイン実行関数"""
    print("=== 有望人材レコメンドシステム ===\n")
    
    try:
        # システム初期化
        print("システムを初期化中...")
        recommender = TalentRecommender()
        print("✓ システム初期化完了\n")
        
        # 人材要件設定
        requirements = {
            "skills": ["機械学習", "Python", "データ分析"],
            "experience": "3年以上",
            "education": "修士以上", 
            "research_area": ["深層学習", "自然言語処理"]
        }
        
        print("検索要件:")
        for key, value in requirements.items():
            print(f"  {key}: {value}")
        print()
        
        # 候補者検索実行
        print("候補者を検索中...")
        results = recommender.find_candidates(requirements)
        
        if not results:
            print("❌ 条件に合致する候補者が見つかりませんでした。")
            return
        
        print(f"✓ {len(results)}名の候補者を発見しました\n")
        
        # 結果表示
        print("=== 検索結果 ===")
        for i, result in enumerate(results, 1):
            print(f"\n【候補者 {i}】")
            print(f"名前: {result.candidate_name}")
            print(f"マッチ度: {result.match_score}点")
            print(f"有望度: {result.potential_score}点")
            print(f"総合スコア: {result.match_score * 0.7 + result.potential_score * 0.3:.1f}点")
            print(f"要約: {result.summary}")
            print(f"強み: {', '.join(result.strengths) if result.strengths else '評価中'}")
            print(f"懸念点: {', '.join(result.concerns) if result.concerns else 'なし'}")
            print(f"情報源: {result.source}")
            print(f"参照URL: {', '.join(result.reference_links) if result.reference_links else 'なし'}")
        
        # アプローチ戦略生成（上位3名）
        if len(results) > 0:
            print(f"\n=== アプローチ戦略（上位{min(3, len(results))}名） ===")
            
            top_candidates = results[:3]
            strategies = recommender.generate_approach_strategies(top_candidates)
            
            for i, result in enumerate(top_candidates, 1):
                strategy = strategies.get(result.candidate_name, "戦略生成中...")
                print(f"\n【{result.candidate_name}】")
                print(f"戦略: {strategy}")
        
        # 結果のエクスポート（オプション）
        export_data = recommender.export_results_to_dict(results)
        print(f"\n=== システム情報 ===")
        print(f"処理時間: 検索完了")
        print(f"候補者総数: {len(results)}名")
        print(f"使用データソース: ResearchMap風データ, LinkedIn風データ")
        print(f"AI分析: Google Gemini Pro")
        
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        print(f"❌ エラーが発生しました: {e}")
        print("\n対処方法:")
        print("1. .env ファイルに GEMINI_API_KEY が正しく設定されているか確認")
        print("2. 仮想環境がアクティベートされているか確認")
        print("3. 必要なライブラリがインストールされているか確認")


if __name__ == "__main__":
    main()