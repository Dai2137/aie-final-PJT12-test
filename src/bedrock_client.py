# bedrock_client.py の実装例

import boto3
import json
from loguru import logger
from typing import Dict, List, Optional # ← この行を追加

class BedrockClient:
    """Amazon Bedrock API クライアント"""

    def __init__(self, region_name: str = "us-east-1"):
        """
        初期化
        Args:
            region_name: Bedrockが有効なリージョン
        """
        # AWS環境で実行する場合、認証情報は自動で設定されることが多い
        self.client = boto3.client(
            service_name="bedrock-runtime", 
            region_name=region_name
        )
        # 確認したNova LiteのモデルIDに書き換える
        self.model_id = "amazon.nova-lite-v1:0"
        logger.info(f"Bedrock APIクライアントを初期化しました (モデル: {self.model_id})")

    def analyze_profile(self, profile_text: str, requirements: dict) -> dict:
        prompt = self._create_analysis_prompt(profile_text, requirements)
        try:
            body = json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}]
            })
            response = self.client.invoke_model(body=body, modelId=self.model_id)
            response_body = json.loads(response.get("body").read())
            
            # 正しい階層をたどってcontentを取得
            output = response_body.get("output", {})
            message = output.get("message", {})
            content_list = message.get("content")

            if content_list and isinstance(content_list, list) and len(content_list) > 0:
                completion = content_list[0].get("text", "")
            else:
                logger.error(f"Bedrock応答からcontentを取得できませんでした。応答: {response_body}")
                completion = ""
            
            return self._parse_analysis_response(completion)
        except Exception as e:
            logger.error(f"Bedrock プロフィール分析エラー: {e}")
            return {
                "match_score": 0, "potential_score": 0,
                "summary": "Bedrockでの分析中にエラーが発生しました",
                "strengths": [], "concerns": []
            }
    
    
    def _create_analysis_prompt(self, profile_text: str, requirements: Dict) -> str:
        """
        分析用プロンプトを作成
        
        Args:
            profile_text: プロフィールテキスト
            requirements: 人材要件
            
        Returns:
            分析用プロンプト
        """
        skills = ", ".join(requirements.get("skills", []))
        experience = requirements.get("experience", "")
        education = requirements.get("education", "")
        research_areas = ", ".join(requirements.get("research_area", []))
        
        prompt = f"""
以下のプロフィール情報と人材要件を比較し、候補者の適合度を評価してください。

【プロフィール情報】
{profile_text}

【人材要件】
- 必要スキル: {skills}
- 経験年数: {experience}
- 教育背景: {education}
- 研究分野: {research_areas}

【評価項目】
1. マッチ度（0-100点）: 要件との適合度
2. 有望度（0-100点）: 将来性や潜在能力
3. 要約（50文字以内）: 候補者の特徴
4. 強み（3項目以内）: 候補者の優れた点
5. 懸念点（3項目以内）: 注意すべき点

以下のJSON形式で回答してください：
{{
    "match_score": 数値,
    "potential_score": 数値,
    "summary": "要約文",
    "strengths": ["強み1", "強み2", "強み3"],
    "concerns": ["懸念点1", "懸念点2", "懸念点3"]
}}
"""
        return prompt

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """
        分析レスポンスを解析
        
        Args:
            response_text: Gemini API からのレスポンステキスト
            
        Returns:
            解析結果辞書
        """
        try:
            import json
            
            # JSONブロックを抽出
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                
                # 必要なキーが存在することを確認
                required_keys = ["match_score", "potential_score", "summary", "strengths", "concerns"]
                for key in required_keys:
                    if key not in result:
                        result[key] = [] if key in ["strengths", "concerns"] else 0
                
                return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON解析エラー: {e}")
        
        # フォールバック
        return {
            "match_score": 50,
            "potential_score": 50,
            "summary": "分析結果の解析に失敗しました",
            "strengths": ["評価困難"],
            "concerns": ["詳細分析が必要"]
        }

    def generate_approach_strategy(self, candidate_info: Dict) -> str:
        try:
            # プロンプトの作成
            prompt = f"""
    以下の候補者情報を基に、効果的なリクルーティングアプローチ戦略を提案してください。
    【候補者情報】
    - 名前: {candidate_info.get('name', '不明')}
    - マッチ度: {candidate_info.get('match_score', 0)}点
    - 有望度: {candidate_info.get('potential_score', 0)}点
    - 要約: {candidate_info.get('summary', '')}
    - 強み: {', '.join(candidate_info.get('strengths', []))}
    - 懸念点: {', '.join(candidate_info.get('concerns', []))}
    【提案内容】
    1. アプローチ方法（メール、LinkedIn、紹介など）
    2. 訴求ポイント（候補者の興味を引く要素）
    3. 初回コンタクトのメッセージ例
    4. 注意点
    150文字以内で簡潔に回答してください。
    """
            # Bedrockへのリクエスト
            body = json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}]
            })
            response = self.client.invoke_model(body=body, modelId=self.model_id)
            response_body = json.loads(response.get("body").read())
            
            # 応答からテキスト部分を抽出
            output = response_body.get("output", {})
            message = output.get("message", {})
            content_list = message.get("content")

            if content_list and isinstance(content_list, list) and len(content_list) > 0:
                return content_list[0].get("text", "戦略の生成に失敗しました。").strip()
            
            return "戦略の生成に失敗しました（空の応答）。"

        except Exception as e:
            logger.error(f"アプローチ戦略生成エラー: {e}")
            return "個別相談により最適なアプローチ方法を検討することをお勧めします。"