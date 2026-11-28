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

- 取り組んだレベル：実装
- やったこと：app/mcp_server.pyを修正し、MCPサーバーにツール（make_quiz）を公開した。また、make_quizのコードを修正し、範囲外になる質問をした場合にreturnでエラーメッセージを返す場合と、例外（raise）にした場合とでtraceの内容を比較した。
- 結果：glossary_make_quizがツールとして追加され、質問に対して当該ツールが呼ばれることや、テストが通ることが確認できた。また、範囲外の質問をした場合、returnで返すメッセージについては[tool return]に出てくることが確認できたが、例外（raise）の場合に[tool error]には設定していたメッセージは出てこず、Error executing tool make_quizという表示が出た。
- 気づき・疑問：ValueErrorが提起された場合にあらかじめ設定していたメッセージが[tool error]には出てこず、Error executing tool make_quizという表示が出てきた理由が分からなかった。
