import tkinter as tk
import random
import time
from itertools import product
import copy  # deepcopy用
from collections import deque # dequeを使うとStageの入力が速い


class GridApp:
    def __init__(self, master, menbers, seating, grid_size=5, cell_size=100,stage_data=[],stage=False):
        self.master = master
        self.menbers = menbers
        self.seating= seating
        self.grid_size = grid_size              # グリッドの行・列数（正方形）
        self.cell_size = cell_size              # 各マスの表示サイズ（ピクセル）
        self.history = []              # 状態履歴（2次元リストのコピーを保持）
        self.history_index = -1        # 現在のインデックス
        self.canvas = tk.Canvas(master, width=grid_size * cell_size * 2, height=grid_size * cell_size)
        self.canvas.pack()

        self.stage_data=stage_data
        if stage==False :self.data = self.generate_grid_data()   # ゲームの初期状態データを生成
        else :self.data = self.set_grid_data()   # ゲームの初期状態データを生成

        self.game_start = False
        self.select_start = None                # 範囲選択の始点（1回目のクリック座標）

        self.stage_data = stage_data
        self.stage = stage

        self.bingos = 0

        self.save_state()              # 初期状態を履歴に保存

        # キーボードショートカット登録
        master.bind("<Control-z>", lambda e: self.undo())
        master.bind("<Control-y>", lambda e: self.redo())
        self.canvas.bind("<Button-1>", self.on_click)  # 左クリックに対するイベントバインド
        self.draw_grid()                        # グリッドの描画

    def save_state(self):
        """現在の状態を履歴に保存"""
        # Undo後に操作したら未来の履歴は削除
        self.history = self.history[:self.history_index + 1]

        self.history.append(copy.deepcopy(self.data))  # 深いコピーで保存
        self.history_index += 1


    def generate_grid_data(self):
        """数字をペアでランダムに配置した2次元グリッドデータを生成"""
        menbers_id = list(range(len(self.menbers)))
        random.shuffle(menbers_id)  # ランダムに並べる
        
        # グリッドに整形
        grid = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                row.append(menbers_id.pop())
            grid.append(row)

        hits = [[0 for x in range(self.grid_size)] for y in range(self.grid_size)]
        seat_hits = [[0 for x in range(len(self.seating[y]))] for y in range(len(self.seating))]
        return [grid,hits,seat_hits]
    
    def set_grid_data(self):
        data = deque(self.stage_data)  # dequeにすると左からのpopが速い

        # グリッドに整形
        menbers_id = data.popleft()
        grid = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                row.append(menbers_id.popleft())
            grid.append(row)
        hits = [[0 for x in range(self.grid_size)] for y in range(self.grid_size)]
        seat_hits = [[0 for x in range(len(self.seating[y]))] for y in range(len(self.grid_size))]
        return [grid,hits,seat_hits]

    def draw_grid(self):
        """現在の状態に基づいてマス目を描画"""
        self.canvas.delete("all")  # 以前の描画を消去

        for i, j in product(range(self.grid_size), repeat=2):
            x0 = j * self.cell_size
            y0 = i * self.cell_size
            x1 = x0 + self.cell_size
            y1 = y0 + self.cell_size
            val = self.data[0][i][j]
            color = "#{:06x}".format(0xAAAA00 if self.data[1][i][j]==0 else 0xAA0000)

            self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color, outline="black")
            self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=self.menbers[val], font=("Arial", 16, "bold"))
            if (j==self.grid_size-1):
                self.canvas.create_line(x1,y0, x1, y1,fill="gray")

        for i in range(len(seating)):
            for j in range(len(seating[i])):
                x0 = j * 70 + 500
                y0 = i * 40 + 200
                x1 = x0 + 70
                y1 = y0 + 40
                color = "#{:06x}".format(0xBBBB00 if self.data[2][i][j]==0 else 0xAA0000)

                self.canvas.create_rectangle(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color, outline="black")
                if (seating[i][j] != -1):
                    self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=self.menbers[seating[i][j]-1], font=("Arial", 12, "bold"))
                if (i==0):
                    self.canvas.create_line(x0, y0, x1, y0,fill="gray")

        if self.select_start:
            x0, y0, x2, y2 = self.select_start
            if (x0 != -1 and y0 != -1):
                x0 = x0 * self.cell_size
                y0 = y0 * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, outline="yellow")
            elif (x2 != -1 and y2 != -1):
                x2 = x2 * 70 + 500
                y2 = y2 * 40 + 200
                x3 = x2 + 70
                y3 = y2 + 40
                self.canvas.create_rectangle(x2 + 5, y2 + 5, x3 - 5, y3 - 5, outline="yellow")

        color = "#{:06x}".format(0xDDDDDD if self.game_start else 0xFF0000)
        out_color = "#{:06x}".format(0xAAAAAA if self.game_start else 0x550000)
        self.canvas.create_rectangle(550,50,650,100,fill=color, outline=out_color)
        self.canvas.create_text(600,75,fill=out_color, text="スタート", font=("Arial", 16, "bold"))

    
        r = int(1/(self.bingos-12.015)+150)
        g = int(0x99*(1-self.bingos/12))
        b = int(1/(self.bingos+1/150)+1/9)
        color = f"#{r:02x}{g:02x}{b:02x}"
        if self.game_start:
            if self.bingos != 12:
                self.canvas.create_text(800,75,fill=color, text=f"{self.bingos}BINGO", font=("Arial", 16, "bold"))
            else :
                self.canvas.create_text(800,75,fill=color, text="BLACK OUT", font=("Arial", 16, "bold"))

    def undo(self):
        """一つ前の状態に戻る"""
        if self.history_index > 0:
            self.history_index -= 1
            self.data = copy.deepcopy(self.history[self.history_index])
            self.draw_grid()

    def redo(self):
        """Undoを取り消して次の状態に進む"""
        if self.history_index + 1 < len(self.history):
            self.history_index += 1
            self.data = copy.deepcopy(self.history[self.history_index])
            self.draw_grid()

    def on_click(self, event):
        """クリック操作で回転範囲を選択"""
        if 550 < event.x and event.x < 650 and 50 < event.y and event.y < 100 and not self.game_start:
            self.game_start = True
            self.history = []
            self.history_index = 0
            self.draw_grid()

        col_0 = event.x // self.cell_size if (event.x < 500) else -1
        row_0 = event.y // self.cell_size if (event.x < 500) else -1
        col_1 = (event.x-500) // 70 if (500 < event.x and 200 < event.y) else -1
        row_1 = (event.y-200) // 40 if (500 < event.x and 200 < event.y) else -1
        if col_0 != -1 or row_0 != -1 or col_1 != -1 or row_1 != -1:
            if not self.select_start:
                # 1回目のクリック：始点を記録
                self.select_start = (col_0, row_0,col_1,row_1)
            else:
                # 2回目のクリック：終点を取得し範囲選択
                x0, y0, x2, y2  = self.select_start
                x1, y1, x3, y3 = col_0, row_0, col_1, row_1
                if x0 != -1 and y0 != -1 and x1 != -1 and y1 != -1:
                    if not self.game_start:
                        id_1 = self.data[0][y0][x0]
                        id_2 = self.data[0][y1][x1]
                        self.data[0][y0][x0] = id_2
                        self.data[0][y1][x1] = id_1
                    elif x0 == x1 and y0 == y1 and self.data[1][y0][x0] == 0:
                        self.hit(False,x0,y0)
                    self.save_state()
                if self.game_start and x2 != -1 and y2 != -1 and x2==x3 and y2==y3 and self.data[2][y2][x2] == 0:
                    self.hit(True,x2,y2)
                    self.save_state()

                self.select_start = None  # 選択リセット
            self.draw_grid()

    def hit(self,is_seating,x,y):
        if is_seating :
            self.data[2][y][x] = 1
            for i, j in product(range(self.grid_size), repeat=2):
                if self.seating[y][x] == self.data[0][i][j]+1:
                    self.data[1][i][j] = 1
                    self.search_bingo(j,i)
                    break
        else :
            self.data[1][y][x] = 1
            self.search_bingo(x,y)
            for i in range(len(seating)):
                for j in range(len(seating[i])):
                    if self.seating[i][j] == self.data[0][y][x]+1:
                        self.data[2][i][j] = 1
                        break

    def search_bingo(self,x,y):
        lines = [True,True,False,False]
        for i in range(-4,5):
            if 0 <= y+i and y+i < 5 and self.data[1][y+i][x] == 0:
                lines[0] = False
                break
        for i in range(-4,5):
            if 0 <= x+i and x+i < 5 and self.data[1][y][x+i] == 0:
                lines[1] = False
                break
        if x==y:
            lines[2] = True
            for i in range(-4,5):
                if 0 <= y+i and y+i < 5 and self.data[1][y+i][x+i] == 0:
                    lines[2] = False
                    break
        if 4-x==y:
            lines[3] = True
            for i in range(-4,5):
                if 0 <= y+i and y+i < 5 and self.data[1][y+i][x-i] == 0:
                    lines[3] = False
                    break
        self.bingos+=lines.count(True)
            

        
            

if __name__ == "__main__":
    menbers = ["安部","池神","石崎","井上","浮津",
               "大島","岡部","亀井","仮屋","河野",
               "川原","窪田","小室","最勝寺","下園",
               "白居","曽根","田井中","高垣","高橋",
               "高本","辰巳","田所","田中","鳥谷尾",
               "長岡","中田","中峰","西村","西本",
               "浜田","飛騨野","福田","藤原","星野",
               "堀口","正田","松本","水谷","溝部",
               "三宅","森野","山添","山中","渡辺"]
    seating = [[43,28,18,14,24,42,16],
               [8,25,37,10,44,39,15],
               [33,41,27,45,31,29,7],
               [11,35,32,13,40,6,19],
               [26,21,12,9,38,17,30],
               [5,36,4,2,3,34,20],
               [-1,-1,23,1,22,-1,-1]]
    root = tk.Tk()
    root.title("居眠りビンゴ")  # ウィンドウタイトル
    app = GridApp(root,menbers,seating)
    root.mainloop()