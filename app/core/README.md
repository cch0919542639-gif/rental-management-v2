# core

放 app factory、config、db、logging、exceptions、auth bootstrap。

## 子區塊

- `app_factory/`
- `config/`
- `db/`
- `logging/`
- `errors/`
- `security/`

所有基礎設施都先從這裡定義，不允許回到巨型入口檔做隱性初始化。
