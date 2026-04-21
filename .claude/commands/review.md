審查目前的修改，然後再 commit。

步驟：

1. 執行 `git diff` 與 `git diff --staged` 查看所有修改

2. 檢查是否有不該進 repo 的大檔案被 staged：
   - `git diff --staged --name-only` 掃描副檔名
   - 危險項目：`.pth`、`.pt`、`data/`、`models/`、`output_images/`、`*.png`（非 sample/）

3. 對每個被修改的 `.py` 執行語法驗證：
   - `python -m py_compile <file>` — 只抓語法錯誤，不需真跑

4. 比對 `requirements.txt` 與被修改的 `.py` 的 import：
   - 若有新的第三方套件 import 但不在 requirements.txt，標示出來

5. 確認 Makefile 與 README 對齊：
   - Makefile 新增或修改的 target，README 指令表是否有同步更新
   - Makefile 的 comment（說明、時間、產出）是否還正確，有無過時描述

6. 確認 .gitignore 完整：
   - 新模組產出的檔案是否已被 ignore（`.pth`、`output_images/`、訓練資料等）
   - 新增的工具或 cache 目錄是否需要加入 ignore
   - 不應 ignore 的檔案是否被意外排除

7. 確認 README 內容準確：
   - 模組清單、指令表、風格名稱與實際程式碼一致
   - 安裝說明是否還正確（套件名稱、是否需要額外步驟）
   - 有無過時的 ⚠️ 警告或說明

8. 列出所有發現的問題（若無則說「看起來沒問題」）

9. 詢問是否繼續 commit
