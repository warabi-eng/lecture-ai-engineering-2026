# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']})<br>aws_aws___search_documentation({'search_phrase': 'What is S3 Versioning', 'topics': ['general']})
- 気づき・疑問：STEP4でAWSのMCPサーバーを使用した際、日本語での入力に対してaws__search documentationのツールが日本語での検索と英語での検索の２回の呼び出しが行われていた。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎
- やったこと：app/mcp_server.pyを修正し、MCPサーバーにツール（get_lecture_summary）を公開した。
- 結果：glossary_get_lecture_summaryがツールとして追加され、質問に対して当該ツールが呼ばれることや、テストが通ることが確認できた。
- 気づき・疑問：過去のの宿題で追加したコードが原因でuv run pytest -pが通らない箇所があった。テストの実施方法や結果の読み方などを学習する必要があると感じた。
