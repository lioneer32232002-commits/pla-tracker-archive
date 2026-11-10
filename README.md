# pla-tracker-archive

Archive of the Republic of China (Taiwan) Ministry of National Defense daily releases
"中共解放軍臺海周邊海、空域動態" (PLA activities in the waters and airspace around Taiwan),
kept as evidence for the figures published on [PLA Tracker](https://pla-tracker.skyfaring.net).

中華民國國防部每日「中共解放軍臺海周邊海、空域動態」公告的原始存檔，作為
[解放軍擾台動態追蹤](https://pla-tracker.skyfaring.net) 每一筆數字的佐證。

## 內容 / Layout

```
mnd/
  index.jsonl                     每則公告一行：公告編號、發布日、存檔路徑、網頁與每個附件的 SHA-256、抓取時間
  2025/2025-12-24_85567/
    page.html                     公告網頁原文（https://www.mnd.gov.tw/news/plaact/85567）
    File_54935.jpg                附件圖片（https://www.mnd.gov.tw/File/54935），原檔未經處理
    File_54936.jpg
scripts/archive.py                每日存檔程式
.github/workflows/archive.yml     每天台灣時間 13:40、21:40 自動執行
```

- 範圍：2020-09-17 起（國防部網站上可取得的最早一則；2022-11-15 以前的格式不同，
  PLA Tracker 主資料沒有使用，2020-09～2022-08 的西南空域通報另存為 swadiz_2020_2022.csv）。
- 只新增、不覆寫：同一則公告存過就不再抓，檔案保持當初取得的樣子。
- 要確認某一天：在 PLA Tracker 的 `data/sources.csv` 查到那天的公告編號，到 `mnd/index.jsonl`
  找同一個編號，比對檔案的 SHA-256；或直接到國防部網站打開同一個網址比對。

## 授權 / License

公告內容與圖片為中華民國國防部公開發布的資訊，著作權依其規定。本 repo 只做原樣保存，
不做任何修改。

The releases and images are public information published by the ROC Ministry of National
Defense and remain subject to its terms. This repository only preserves them unchanged.
