# maintenance module

## 責任

- 維修工單與待修狀態的正式邊界
- 不再用 `Room.status` 或虛擬 tenant 名稱承載待修語義

## 現況

- 第一版只建立模組邊界與操作入口
- 正式資料 schema 尚未凍結，暫不建立 maintenance table

## 注意

- 不得自行發明維修狀態表結構
- 若要正式落地，需先補 maintenance data contract
