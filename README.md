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
- **AI/LLM**: Amazon Nova Lite
- **データソース**: GitHubの公開情報（プロフィール）

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
# GEMINI_API_KEY=your_gemini_api_key
```

## 使用方法

### 基本的な使用例
```python
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
    print(f"参照URL: {', '.join(result.reference_links) if result.reference_links else 'なし'}")```

## プロジェクト構造

```
talent_recommender/
├── src/
│   ├── __init__.py
│   ├── talent_recommender.py    # メインシステム
│   ├── data_collector.py        # データ収集モジュール
│   ├── matching_engine.py       # マッチングエンジン
│   ├── requirements_fetcher.py  # 人材要件取得
│   └── bedrock_client.py         # bedrock クライアント
├── requirements.txt            # 依存関係
├── .env.example               # 環境変数テンプレート
└── README.md                  # このファイル
```

## 開発ロードマップ

### Phase 1: 基本機能
- [ ] プロジェクト構造の設計
- [ ] 人材要件入力システム
- [ ] Nova Lite連携
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
- [Nova Lite API ドキュメント](https://docs.aws.amazon.com/bedrock/latest/userguide/nova-lite-api.html)

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


## システム特徴

### 🎯 高精度マッチング
- Amazon Nova Lite AIによる詳細なプロフィール分析
- 複数指標による総合評価（マッチ度・有望度）
- 候補者の強みと懸念点の明確化

### 📊 多様なデータソース
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

<!-- - 現在はモックデータを使用（実際のAPI接続時は利用規約を確認） -->
- Amazon Nova Lite APIキーの設定が必要
- プライバシー保護に配慮した設計

## ライセンス

このプロジェクトは研究目的で作成されています。