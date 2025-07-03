#!/usr/bin/env python3
"""
有望人材レコメンドシステム実行例
"""

from dotenv import load_dotenv
import os
import sys
from loguru import logger

# 1. 最初に環境変数を読み込む
load_dotenv()

# 2. srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 3. 自作モジュールをインポート
from talent_recommender import TalentRecommender
from requirements_fetcher import fetch_text_from_url


def main():
    """メイン実行関数"""
    print("=== 有望人材レコメンドシステム ===\n")
    
    try:
        # 4. .envからPATを読み込み、存在を確認
        github_pat = os.getenv("GITHUB_PAT")
        if not github_pat:
            logger.error("GITHUB_PATが.envファイルに設定されていません。")
            print("❌ エラー: .envファイルにGITHUB_PATを設定してください。")
            return

        print("システムを初期化中...")
        # 5. PATを引数として渡す
        recommender = TalentRecommender(github_pat=github_pat)
        print("✓ システム初期化完了\n")
        
        
        # 1. 人材要件をWebページから取得
        print("人材要件をWebから取得中...")
        requirement_url = "https://herp.careers/v1/weblab/r-pnKT2vTAb7"
        raw_text = fetch_text_from_url(requirement_url)
        if not raw_text:
            print("❌ 人材要件の取得に失敗しました。")
            return
        
        # 2. 取得したテキストを分析し、キーワードを抽出
        requirements = recommender.analyze_requirements_from_text(raw_text)
        if not requirements:
            print("❌ 人材要件の分析に失敗しました。")
            return

        print("▼ 抽出された検索キーワード")
        print(requirements["skills"])
        print()

        # 3. 抽出されたキーワードで候補者を検索
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
        # print(f"AI分析: Google Gemini Pro")
        
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        print(f"❌ エラーが発生しました: {e}")
        print("\n対処方法:")
        # print("1. .env ファイルに GEMINI_API_KEY が正しく設定されているか確認")
        print("2. 仮想環境がアクティベートされているか確認")
        print("3. 必要なライブラリがインストールされているか確認")


if __name__ == "__main__":
    main()