# Git 使用說明（簡易版）

## Git 是什麼？
Git 就像專案的「**修改紀錄簿**」：每次「提交」都會記下誰在什麼時候改了什麼，改壞了也能回到以前的版本。
GitHub 則是放在網路上的「**共用櫃子**」，大家都從這裡拿最新版本，也把自己改好的東西放回這裡。

## 先認識四個詞
| 詞 | 意思 |
|---|---|
| **存檔** | 在編輯器按 Ctrl+S（Mac 是 Cmd+S），跟平常一樣。只存在你的電腦，Git 還沒記錄。 |
| **提交** | 用 `git commit` 把修改**寫進紀錄簿**。存檔之後還要提交，Git 才算記住。 |
| **主版本（main）** | 大家共用的正式版本。 |
| **草稿（分支）** | 你自己的工作副本。改壞了也不會影響別人。 |

## 三條規則（一定要遵守）
1. **不要直接改主版本**：先開一份自己的草稿再改，改好請人看過才放回主版本。
2. **不要上傳真實資料**：員工姓名、工作量、工單、Excel 檔都放在 `data/` 資料夾，那裡的東西本來就不會上傳。上傳前先看一下清單，有疑問就停下來問人。
3. **提交時寫清楚改了什麼**：別人一看就知道你做了什麼。

---

## 每次工作的 5 個步驟

在專案資料夾裡打開終端機（Terminal），照順序輸入：

**① 拿最新的主版本**
```
git switch main
git pull
```
如果這裡出現錯誤，看下面的「狀況一」。

**② 開一份自己的草稿**（名字自己取，英文、不要有空格）
```
git switch -c 我的名字-要做的事
```
例：`git switch -c amy-update-glossary`

**③ 修改檔案並存檔**（照平常的方式編輯，按 Ctrl+S）

**④ 提交**
```
git status
git add .
git commit -m "這次改了什麼"
```
輸入 `git status` 後先檢查兩件事：
- **第一行**應該是 `On branch 你的草稿名字`。如果寫的是 `On branch main`，先停下來，看「狀況三」。
- **檔案清單**裡如果出現 `data/` 或 Excel 檔，先停下來，找技術同事。

**⑤ 上傳，請人檢查**
```
git push -u origin 我的名字-要做的事
```
接著打開 GitHub 網頁，按綠色的「**Compare & pull request**」，寫一句說明後送出。
有人確認沒問題，就會把你的修改放進主版本。

---

## 範例：Amy 要修改名詞說明文件

```
git switch main
git pull
git switch -c amy-update-glossary
```
（Amy 打開 `brain/_core/glossary.md`，加了一個新名詞，按 Ctrl+S 存檔）
```
git status
git add .
git commit -m "名詞說明：新增「進線量」的定義"
git push -u origin amy-update-glossary
```
（到 GitHub 網頁按「Compare & pull request」→ 送出 → 等同事確認）

**提交說明怎麼寫：**
- 好：`名詞說明：新增「進線量」的定義`、`修正 DW 報表 Promo 少算`
- 不好：`更新`、`修改`、`aaa`（別人看不出改了什麼）

---

## 三種常見狀況與解法

> 這些狀況**都不會弄壞任何東西**，照著做就好。做到一半不確定，就截圖找技術同事。

### 狀況一：忘了提交，就想去拿新版本
**什麼時候會遇到：** 做步驟 ① 的 `git switch main` 時，畫面出現：
```
error: Your local changes to the following files would be overwritten by checkout
```
**意思：** 你上次的修改有存檔，但還沒提交。Git 怕切換時弄丟這些修改，所以先擋下來。

**解法：** 留在原本的草稿，把上次的修改先提交，再重新做步驟 ①。
```
git status
git add .
git commit -m "上次改了什麼"
git switch main
git pull
```
（`git status` 第一行應該是你的草稿名字。如果是 `main`，改看「狀況三」。）

### 狀況二：草稿太舊，跟主版本衝突
**什麼時候會遇到：** 送出檢查請求後，GitHub 網頁顯示「**This branch has conflicts**」。
**意思：** 你開草稿之後，別人也改了同一個檔案的同一段。Git 不知道要留哪個版本，要你決定。

**解法：**

第 1 步：把最新的主版本拿進你的草稿
```
git switch main
git pull
git switch 我的名字-要做的事
git merge main
```
- 沒有出現 `CONFLICT`：直接輸入 `git push`，完成。
- 出現 `CONFLICT (content): Merge conflict in 某個檔案`：繼續第 2 步。

第 2 步：打開畫面上寫的那個檔案，會看到這樣的標記：
```
<<<<<<< HEAD
你的版本
=======
別人的版本（主版本）
>>>>>>> main
```
決定要留哪些內容，改成正確的樣子，並**刪掉 `<<<<<<<`、`=======`、`>>>>>>>` 這三行標記**，然後存檔。

第 3 步：提交並上傳
```
git add 那個檔案
git commit -m "解決衝突：說明你留了哪個版本"
git push
```

**想放棄、回到合併前的樣子：** 在第 3 步之前輸入 `git merge --abort`。

**範例**（Amy 的草稿太舊）：
```
git switch main
git pull
git switch amy-update-glossary
git merge main
（出現 CONFLICT → 打開 glossary.md，整理成正確內容、刪掉三行標記、存檔）
git add brain/_core/glossary.md
git commit -m "解決衝突：保留兩邊新增的名詞"
git push
```

### 狀況三：不小心在主版本上改了東西
**什麼時候會遇到：** 輸入 `git status`，第一行寫的是 `On branch main`，下面卻列出你改過的檔案。
**意思：** 你忘了做步驟 ②，直接在主版本上改了。

**解法：還沒提交的話**，直接開一份草稿，修改會自動一起帶過去：
```
git switch -c 我的名字-要做的事
```
然後從步驟 ④ 繼續就好。

**如果已經提交了**（已經輸入過 `git commit`）：先不要輸入 `git push`，截圖找技術同事處理。

---

## 其他問題

| 狀況 | 做法 |
|---|---|
| 不確定自己現在在主版本還是草稿 | 輸入 `git status`，看第一行的 `On branch ...` |
| 不小心把資料檔上傳了 | **立刻通知負責人**，不要自己處理 |
| 看不懂畫面上的訊息 | 截圖給技術同事 |

> 修改 `brain/` 裡的程式或規則設定後，還要跑檢查工具（`check_all.py` 等）。這部分由**技術同事在合併前處理**，非技術成員不用擔心。
