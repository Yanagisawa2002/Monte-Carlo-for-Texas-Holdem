import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from poker_calculator import Card, Deck, HandEvaluator, PokerWinRateCalculator
import threading
import random

class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("德州扑克胜率计算器")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TCombobox", font=("SimHei", 10))

        # 定义牌的花色和点数
        self.suits = ['s', 'h', 'd', 'c']
        self.suit_names = {'s': '黑桃(♠)', 'h': '红桃(♥)', 'd': '方块(♦)', 'c': '梅花(♣)'}
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

        # 创建计算器实例
        self.calculator = None
        self.simulations = 10000
        self.is_calculating = False

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建输入区域
        self.create_input_section()

        # 创建结果区域
        self.create_result_section()

        # 创建进度条
        self.create_progress_section()

    def create_input_section(self):
        input_frame = ttk.LabelFrame(self.main_frame, text="输入参数", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 玩家数量
        ttk.Label(input_frame, text="玩家总数 (2-10):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_players_var = tk.StringVar(value="2")
        num_players_combo = ttk.Combobox(input_frame, textvariable=self.num_players_var, values=[str(i) for i in range(2, 11)], width=5)
        num_players_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # 游戏阶段选择
        ttk.Label(input_frame, text="开牌阶段:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.stage_var = tk.StringVar(value="翻牌前")
        stage_combo = ttk.Combobox(input_frame, textvariable=self.stage_var, 
                                   values=["翻牌前", "翻牌后", "转牌后", "河牌后"], width=10)
        stage_combo.grid(row=0, column=3, sticky=tk.W, pady=5)

        # 手牌输入 - 使用下拉菜单选择
        ttk.Label(input_frame, text="您的手牌:").grid(row=1, column=0, sticky=tk.W, pady=5)

        # 第一张手牌
        ttk.Label(input_frame, text="第一张牌:").grid(row=1, column=1, sticky=tk.W, pady=5)
        self.hand1_suit_var = tk.StringVar(value=self.suits[0])
        hand1_suit_combo = ttk.Combobox(input_frame, textvariable=self.hand1_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        hand1_suit_combo.grid(row=1, column=2, sticky=tk.W, pady=5)

        self.hand1_rank_var = tk.StringVar(value=self.ranks[12])  # 默认A
        hand1_rank_combo = ttk.Combobox(input_frame, textvariable=self.hand1_rank_var, 
                                       values=self.ranks, width=5)
        hand1_rank_combo.grid(row=1, column=3, sticky=tk.W, pady=5)

        # 第二张手牌
        ttk.Label(input_frame, text="第二张牌:").grid(row=1, column=4, sticky=tk.W, pady=5)
        self.hand2_suit_var = tk.StringVar(value=self.suits[1])
        hand2_suit_combo = ttk.Combobox(input_frame, textvariable=self.hand2_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        hand2_suit_combo.grid(row=1, column=5, sticky=tk.W, pady=5)

        self.hand2_rank_var = tk.StringVar(value=self.ranks[11])  # 默认K
        hand2_rank_combo = ttk.Combobox(input_frame, textvariable=self.hand2_rank_var, 
                                       values=self.ranks, width=5)
        hand2_rank_combo.grid(row=1, column=6, sticky=tk.W, pady=5)

        # 公牌输入 - 翻牌 (3张)
        ttk.Label(input_frame, text="翻牌 (3张):").grid(row=2, column=0, sticky=tk.W, pady=5)

        # 翻牌1
        ttk.Label(input_frame, text="第1张:").grid(row=2, column=1, sticky=tk.W, pady=5)
        self.flop1_suit_var = tk.StringVar(value=self.suits[0])
        flop1_suit_combo = ttk.Combobox(input_frame, textvariable=self.flop1_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        flop1_suit_combo.grid(row=2, column=2, sticky=tk.W, pady=5)

        self.flop1_rank_var = tk.StringVar(value=self.ranks[0])  # 默认2
        flop1_rank_combo = ttk.Combobox(input_frame, textvariable=self.flop1_rank_var, 
                                       values=self.ranks, width=5)
        flop1_rank_combo.grid(row=2, column=3, sticky=tk.W, pady=5)

        # 翻牌2
        ttk.Label(input_frame, text="第2张:").grid(row=2, column=4, sticky=tk.W, pady=5)
        self.flop2_suit_var = tk.StringVar(value=self.suits[1])
        flop2_suit_combo = ttk.Combobox(input_frame, textvariable=self.flop2_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        flop2_suit_combo.grid(row=2, column=5, sticky=tk.W, pady=5)

        self.flop2_rank_var = tk.StringVar(value=self.ranks[1])  # 默认3
        flop2_rank_combo = ttk.Combobox(input_frame, textvariable=self.flop2_rank_var, 
                                       values=self.ranks, width=5)
        flop2_rank_combo.grid(row=2, column=6, sticky=tk.W, pady=5)

        # 翻牌3
        ttk.Label(input_frame, text="第3张:").grid(row=2, column=7, sticky=tk.W, pady=5)
        self.flop3_suit_var = tk.StringVar(value=self.suits[2])
        flop3_suit_combo = ttk.Combobox(input_frame, textvariable=self.flop3_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        flop3_suit_combo.grid(row=2, column=8, sticky=tk.W, pady=5)

        self.flop3_rank_var = tk.StringVar(value=self.ranks[3])  # 默认4
        flop3_rank_combo = ttk.Combobox(input_frame, textvariable=self.flop3_rank_var, 
                                       values=self.ranks, width=5)
        flop3_rank_combo.grid(row=2, column=9, sticky=tk.W, pady=5)

        # 公牌输入 - 转牌 (1张)
        ttk.Label(input_frame, text="转牌 (1张):").grid(row=3, column=0, sticky=tk.W, pady=5)

        ttk.Label(input_frame, text="牌:").grid(row=3, column=1, sticky=tk.W, pady=5)
        self.turn_suit_var = tk.StringVar(value=self.suits[3])
        turn_suit_combo = ttk.Combobox(input_frame, textvariable=self.turn_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        turn_suit_combo.grid(row=3, column=2, sticky=tk.W, pady=5)

        self.turn_rank_var = tk.StringVar(value=self.ranks[4])  # 默认5
        turn_rank_combo = ttk.Combobox(input_frame, textvariable=self.turn_rank_var, 
                                       values=self.ranks, width=5)
        turn_rank_combo.grid(row=3, column=3, sticky=tk.W, pady=5)

        # 公牌输入 - 河牌 (1张)
        ttk.Label(input_frame, text="河牌 (1张):").grid(row=4, column=0, sticky=tk.W, pady=5)

        ttk.Label(input_frame, text="牌:").grid(row=4, column=1, sticky=tk.W, pady=5)
        self.river_suit_var = tk.StringVar(value=self.suits[0])
        river_suit_combo = ttk.Combobox(input_frame, textvariable=self.river_suit_var, 
                                       values=list(self.suit_names.values()), width=8)
        river_suit_combo.grid(row=4, column=2, sticky=tk.W, pady=5)

        self.river_rank_var = tk.StringVar(value=self.ranks[5])  # 默认6
        river_rank_combo = ttk.Combobox(input_frame, textvariable=self.river_rank_var, 
                                       values=self.ranks, width=5)
        river_rank_combo.grid(row=4, column=3, sticky=tk.W, pady=5)

        # 模拟精度
        ttk.Label(input_frame, text="模拟精度:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.precision_var = tk.StringVar(value="平衡模式 (10,000次)")
        precision_combo = ttk.Combobox(input_frame, textvariable=self.precision_var, 
                                       values=["快速模式 (1,000次)", "平衡模式 (10,000次)", "精确模式 (100,000次)", "自定义次数"], width=20)
        precision_combo.grid(row=5, column=1, sticky=tk.W, pady=5)

        # 自定义次数输入框 (默认隐藏)
        self.custom_sim_var = tk.StringVar(value="10000")
        self.custom_sim_entry = ttk.Entry(input_frame, textvariable=self.custom_sim_var, width=10)
        # 将在精度选择改变时显示/隐藏

        # 绑定精度选择事件
        precision_combo.bind("<<ComboboxSelected>>", self.on_precision_change)

        # 按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=6, column=0, columnspan=10, pady=10)

        ttk.Button(button_frame, text="计算胜率", command=self.calculate_win_rate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置", command=self.reset_inputs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=root.quit).pack(side=tk.RIGHT, padx=5)

    def on_precision_change(self, event):
        if self.precision_var.get() == "自定义次数":
            self.custom_sim_entry.grid(row=5, column=2, sticky=tk.W, pady=5)
        else:
            self.custom_sim_entry.grid_remove()

    def create_result_section(self):
        result_frame = ttk.LabelFrame(self.main_frame, text="计算结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 当前状态
        ttk.Label(result_frame, text="当前状态:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="等待输入...")
        ttk.Label(result_frame, textvariable=self.status_var, foreground="blue").grid(row=0, column=1, sticky=tk.W, pady=5)

        # 胜率
        ttk.Label(result_frame, text="胜率:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.win_rate_var = tk.StringVar(value="0.00%")
        ttk.Label(result_frame, textvariable=self.win_rate_var, font=("SimHei", 12, "bold")).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 优势倍数
        ttk.Label(result_frame, text="优势倍数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.advantage_var = tk.StringVar(value="0.0x")
        ttk.Label(result_frame, textvariable=self.advantage_var).grid(row=2, column=1, sticky=tk.W, pady=5)

        # 策略建议
        ttk.Label(result_frame, text="策略建议:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.strategy_var = tk.StringVar(value="")
        ttk.Label(result_frame, textvariable=self.strategy_var, wraplength=400).grid(row=3, column=1, sticky=tk.W, pady=5)

        # 公牌显示
        ttk.Label(result_frame, text="当前公牌:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.community_cards_var = tk.StringVar(value="无")
        ttk.Label(result_frame, textvariable=self.community_cards_var).grid(row=4, column=1, sticky=tk.W, pady=5)

        # 模拟次数
        ttk.Label(result_frame, text="模拟次数:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.sim_count_var = tk.StringVar(value="0")
        ttk.Label(result_frame, textvariable=self.sim_count_var).grid(row=5, column=1, sticky=tk.W, pady=5)

    def create_progress_section(self):
        progress_frame = ttk.LabelFrame(self.main_frame, text="计算进度", padding="10")
        progress_frame.pack(fill=tk.X)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_text_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.progress_text_var).pack()

    def reset_inputs(self):
        self.num_players_var.set("2")
        # 重置手牌
        self.hand1_suit_var.set(list(self.suit_names.values())[0])
        self.hand1_rank_var.set(self.ranks[12])  # A
        self.hand2_suit_var.set(list(self.suit_names.values())[1])
        self.hand2_rank_var.set(self.ranks[11])  # K

        # 重置翻牌
        self.flop1_suit_var.set(list(self.suit_names.values())[0])
        self.flop1_rank_var.set(self.ranks[0])  # 2
        self.flop2_suit_var.set(list(self.suit_names.values())[1])
        self.flop2_rank_var.set(self.ranks[1])  # 3
        self.flop3_suit_var.set(list(self.suit_names.values())[2])
        self.flop3_rank_var.set(self.ranks[3])  # 4

        # 重置转牌
        self.turn_suit_var.set(list(self.suit_names.values())[3])
        self.turn_rank_var.set(self.ranks[4])  # 5

        # 重置河牌
        self.river_suit_var.set(list(self.suit_names.values())[0])
        self.river_rank_var.set(self.ranks[5])  # 6

        self.precision_var.set("平衡模式 (10,000次)")
        self.custom_sim_entry.grid_remove()
        self.status_var.set("等待输入...")
        self.win_rate_var.set("0.00%")
        self.advantage_var.set("0.0x")
        self.strategy_var.set("")
        self.community_cards_var.set("无")
        self.sim_count_var.set("0")
        self.progress_var.set(0)
        self.progress_text_var.set("就绪")
        self.calculator = None
        self.is_calculating = False

    def set_simulations(self):
        precision = self.precision_var.get()
        if precision == "快速模式 (1,000次)":
            self.simulations = 1000
        elif precision == "平衡模式 (10,000次)":
            self.simulations = 10000
        elif precision == "精确模式 (100,000次)":
            self.simulations = 100000
        elif precision == "自定义次数":
            try:
                custom = int(self.custom_sim_var.get())
                if 100 <= custom <= 1000000:
                    self.simulations = custom
                else:
                    messagebox.showerror("错误", "自定义次数必须在100到1,000,000之间")
                    return False
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
                return False
        return True

    def get_suit_key(self, suit_name):
        # 从花色名称获取对应的键
        for key, name in self.suit_names.items():
            if name == suit_name:
                return key
        return 's'  # 默认返回黑桃

    def calculate_win_rate(self):
        if self.is_calculating:
            messagebox.showinfo("提示", "计算已在进行中，请等待完成")
            return

        # 设置模拟次数
        if not self.set_simulations():
            return

        # 获取玩家数量
        try:
            num_players = int(self.num_players_var.get())
            if not 2 <= num_players <= 10:
                messagebox.showerror("错误", "玩家数量必须在2到10之间")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的玩家数量")
            return

        # 构建手牌
        try:
            hand1_suit = self.get_suit_key(self.hand1_suit_var.get())
            hand1_rank = self.hand1_rank_var.get()
            hand1 = f"{hand1_rank}{hand1_suit}"

            hand2_suit = self.get_suit_key(self.hand2_suit_var.get())
            hand2_rank = self.hand2_rank_var.get()
            hand2 = f"{hand2_rank}{hand2_suit}"

            hand_input = [hand1, hand2]
        except Exception as e:
            messagebox.showerror("错误", f"手牌构建错误: {str(e)}")
            return

        # 创建计算器实例
        try:
            self.calculator = PokerWinRateCalculator(num_players, hand_input)
        except ValueError as e:
            messagebox.showerror("错误", f"手牌输入错误: {e}")
            return

        # 添加公牌
        try:
            stage = self.stage_var.get()
            community_cards = []

            if stage in ["翻牌后", "转牌后", "河牌后"]:
                # 翻牌
                flop1_suit = self.get_suit_key(self.flop1_suit_var.get())
                flop1_rank = self.flop1_rank_var.get()
                flop1 = f"{flop1_rank}{flop1_suit}"

                flop2_suit = self.get_suit_key(self.flop2_suit_var.get())
                flop2_rank = self.flop2_rank_var.get()
                flop2 = f"{flop2_rank}{flop2_suit}"

                flop3_suit = self.get_suit_key(self.flop3_suit_var.get())
                flop3_rank = self.flop3_rank_var.get()
                flop3 = f"{flop3_rank}{flop3_suit}"

                community_cards.extend([flop1, flop2, flop3])

            if stage in ["转牌后", "河牌后"]:
                # 转牌
                turn_suit = self.get_suit_key(self.turn_suit_var.get())
                turn_rank = self.turn_rank_var.get()
                turn = f"{turn_rank}{turn_suit}"
                community_cards.append(turn)

            if stage == "河牌后":
                # 河牌
                river_suit = self.get_suit_key(self.river_suit_var.get())
                river_rank = self.river_rank_var.get()
                river = f"{river_rank}{river_suit}"
                community_cards.append(river)

            if community_cards:
                self.calculator.add_community_cards(community_cards)

        except ValueError as e:
            messagebox.showerror("错误", f"公牌输入错误: {e}")
            return

        # 更新状态
        self.status_var.set("计算中...")
        self.is_calculating = True
        self.sim_count_var.set(str(self.simulations))

        # 显示当前公牌和阶段
        stage = self.stage_var.get()
        if len(self.calculator.community_cards) > 0:
            self.community_cards_var.set(f"{stage} - " + ", ".join(str(c) for c in self.calculator.community_cards))
        else:
            self.community_cards_var.set(f"{stage} - 无")

        # 在新线程中执行计算
        threading.Thread(target=self.run_calculation).start()

    def progress_callback(self, current, total):
        # 更新进度条
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.progress_text_var.set(f"已完成 {current}/{total} 次模拟")
        self.root.update_idletasks()

    def run_calculation(self):
        try:
            start_time = time.time()
            win_rate = self.calculator.calculate_win_rate(self.simulations, self.progress_callback)
            elapsed_time = time.time() - start_time

            # 计算优势倍数
            avg_win_rate = 1 / self.calculator.num_players
            win_advantage = win_rate / avg_win_rate if avg_win_rate > 0 else 0

            # 生成策略建议
            if win_advantage >= 2.0:
                strategy = "强烈建议加注"
            elif win_advantage >= 1.5:
                strategy = "建议跟注"
            elif win_advantage >= 1.0:
                strategy = "谨慎跟注"
            else:
                strategy = "建议弃牌"

            # 更新UI
            self.root.after(0, lambda: self.update_results(win_rate, win_advantage, strategy, elapsed_time))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("计算错误", f"计算过程中出错: {str(e)}"))
        finally:
            self.is_calculating = False
            self.root.after(0, lambda: self.status_var.set("计算完成"))

    def update_results(self, win_rate, win_advantage, strategy, elapsed_time):
        self.win_rate_var.set(f"{win_rate:.2%}")
        self.advantage_var.set(f"{win_advantage:.1f}x")
        self.strategy_var.set(f"{strategy} (基于{self.calculator.num_players}名玩家的竞争环境)")
        self.progress_text_var.set(f"计算完成 (耗时: {elapsed_time:.2f} 秒)")

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()