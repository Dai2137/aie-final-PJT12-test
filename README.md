# 有望人材のレコメンドシステム

プロジェクトの詳細は、所定のドキュメントを確認すること。

## 主要機能

### 1. 人材要件入力・マッチングシステム
- 人材要件の入力インターフェース
- 候補人材の情報出力
- 出力内容：
  - 人材プロフィールの要約
  - 参照情報のリンク
  - 人材要件との一致度
  - 人材の有望度スコア

### 2. パフォーマンス要件
- ユーザー入力後、数分以内での結果出力
- リアルタイムでの人材情報分析

### 3. 発展的機能（オプション）
- **人材ネットワーク可視化**: インタラクティブな人材関係性の表示
- **アプローチ戦略立案**: 効果的なリクルーティング戦略の提案

## 技術スタック

- **言語**: Python
- **仮想環境**: uv venv
- **パッケージ管理**: uv pip
- **AI/LLM**: Google Gemini API
- **データソース**: SNS、ResearchMap等の公開情報

## セットアップ

### 1. 仮想環境の作成
```bash
uv venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール
```bash
uv pip install -r requirements.txt
```

### 3. 環境変数の設定
```bash
# .env ファイルを作成し、以下を設定
GEMINI_API_KEY=your_gemini_api_key
```

## 使用方法

### 基本的な使用例
```python
from talent_recommender import TalentRecommender

# システムの初期化
recommender = TalentRecommender()

# 人材要件の設定
requirements = {
    "skills": ["機械学習", "Python", "データ分析"],
    "experience": "3年以上",
    "education": "修士以上",
    "research_area": ["深層学習", "自然言語処理"]
}

# 人材レコメンドの実行
candidates = recommender.find_candidates(requirements)

# 結果の表示
for candidate in candidates:
    print(f"名前: {candidate.name}")
    print(f"マッチ度: {candidate.match_score}")
    print(f"有望度: {candidate.potential_score}")
    print(f"プロフィール: {candidate.profile_summary}")
    print(f"参照URL: {candidate.reference_links}")
    print("---")
```

## プロジェクト構造

```
talent_recommender/
├── src/
│   ├── __init__.py
│   ├── talent_recommender.py    # メインシステム
│   ├── data_collector.py        # データ収集モジュール
│   ├── profile_analyzer.py      # プロフィール分析
│   ├── matching_engine.py       # マッチングエンジン
│   └── gemini_client.py         # Gemini API クライアント
├── data/
│   └── sample_data/             # サンプルデータ
├── tests/
│   └── test_*.py               # テストファイル
├── requirements.txt            # 依存関係
├── .env.example               # 環境変数テンプレート
└── README.md                  # このファイル
```

## 開発ロードマップ

### Phase 1: 基本機能
- [ ] プロジェクト構造の設計
- [ ] 人材要件入力システム
- [ ] Gemini API連携
- [ ] 基本的なマッチング機能

### Phase 2: 高度な分析
- [ ] プロフィール詳細分析
- [ ] 多次元マッチングアルゴリズム
- [ ] 有望度スコア算出

### Phase 3: 発展機能
- [ ] 人材ネットワーク可視化
- [ ] アプローチ戦略立案
- [ ] インタラクティブUI

## 参考リンク

- [募集要項例](https://herp.careers/v1/weblab/r-pnKT2vTAb7)
- Google Gemini API ドキュメント
- ResearchMap API (利用可能な場合)

## 実行方法

### 1. 環境設定
```bash
# 仮想環境のアクティブ化
source .venv/bin/activate

# 環境変数ファイルの作成
cp .env.example .env
# .env ファイルを編集してGEMINI_API_KEYを設定
```

### 2. サンプル実行
```bash
# サンプルプログラムの実行
python example.py
```

### 3. カスタム実行
```python
from src.talent_recommender import TalentRecommender

# システム初期化
recommender = TalentRecommender()

# 検索要件設定
requirements = {
    "skills": ["機械学習", "Python", "データ分析"],
    "experience": "3年以上",
    "education": "修士以上",
    "research_area": ["深層学習", "自然言語処理"]
}

# 候補者検索
results = recommender.find_candidates(requirements)

# 結果表示
for result in results:
    print(f"名前: {result.candidate_name}")
    print(f"マッチ度: {result.match_score}点")
    print(f"有望度: {result.potential_score}点")
```

## システム特徴

### 🎯 高精度マッチング
- Google Gemini AIによる詳細なプロフィール分析
- 複数指標による総合評価（マッチ度・有望度）
- 候補者の強みと懸念点の明確化

### 📊 多様なデータソース
- ResearchMap風データ（研究者情報）
- LinkedIn風データ（職歴・スキル情報）
- GitHub API連携（開発者実績）

### 🚀 効率的な運用
- 数分以内での候補者抽出
- 自動ランキング・フィルタリング
- アプローチ戦略の自動生成

## テスト結果

システムテストにより以下の動作を確認済み：
- ✅ モジュール正常インポート
- ✅ データ収集機能（2件のサンプルデータ取得）
- ✅ マッチングエンジン（80点のスコア算出例）
- ✅ 全体システム統合動作

## 注意事項

- 現在はモックデータを使用（実際のAPI接続時は利用規約を確認）
- Google Gemini APIキーの設定が必要
- プライバシー保護に配慮した設計

## ライセンス

このプロジェクトは研究目的で作成されています。