"""OP Workforce AI 共用程式庫（brain/_core/lib/opbrain）。

所有 Skill 的腳本都透過這個套件取得：專案路徑、統一結束碼、設定檔讀取、
Roster 讀取、.env 設定。規則的「意義與理由」寫在各 Skill 的文件裡，
這裡只負責「怎麼做」。

腳本使用方式（放在 brain/<skill>/scripts/ 底下的腳本開頭）：
    import _bootstrap  # noqa: F401  （把本套件加入 sys.path）
    from opbrain import common, paths
"""
