import sys
import time
import threading
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QLineEdit, QPushButton, QProgressBar, 
                            QGroupBox, QMessageBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')
from poker_calculator import Card, Deck, HandEvaluator, PokerWinRateCalculator

class ProgressUpdater(QThread):
    progress_updated = pyqtSignal(int, int)

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def update(self, current, total):
        self.progress_updated.emit(current, total)

class PokerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("德州扑克胜率计算器")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(800, 500)

        # 设置中文字体
        font = QFont("SimHei", 10)
        QApplication.setFont(font)

        # 定义牌的花色和点数
        self.suits = ['s', 'h', 'd', 'c']
        self.suit_names = {'s': '黑桃(♠)', 'h': '红桃(♥)', 'd': '方块(♦)', 'c': '梅花(♣)'}
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

        # 创建计算器实例
        self.calculator = None
        self.simulations = 10000
        self.is_calculating = False

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        # 创建输入区域
        self.create_input_section()

        # 创建结果区域
        self.create_result_section()

        # 创建进度条
        self.create_progress_section()

        # 创建进度更新器
        self.progress_updater = ProgressUpdater(self.update_progress)
        self.progress_updater.progress_updated.connect(self.on_progress_updated)

    def create_input_section(self):
        input_group = QGroupBox("输入参数")
        input_layout = QGridLayout()
        input_group.setLayout(input_layout)

        # 玩家数量
        input_layout.addWidget(QLabel("玩家总数 (2-10):"), 0, 0, Qt.AlignLeft)
        self.num_players_combo = QComboBox()
        self.num_players_combo.addItems([str(i) for i in range(2, 11)])
        self.num_players_combo.setCurrentText("2")
        input_layout.addWidget(self.num_players_combo, 0, 1, Qt.AlignLeft)

        # 游戏阶段选择
        input_layout.addWidget(QLabel("开牌阶段:"), 0, 2, Qt.AlignLeft)
        self.stage_combo = QComboBox()
        self.stage_combo.addItems(["翻牌前", "翻牌后", "转牌后", "河牌后"])
        self.stage_combo.setCurrentText("翻牌前")
        input_layout.addWidget(self.stage_combo, 0, 3, Qt.AlignLeft)

        # 手牌输入
        input_layout.addWidget(QLabel("您的手牌:"), 1, 0, Qt.AlignLeft)

        # 第一张手牌
        input_layout.addWidget(QLabel("第一张牌:"), 1, 1, Qt.AlignLeft)
        self.hand1_suit_combo = QComboBox()
        self.hand1_suit_combo.addItems(list(self.suit_names.values()))
        input_layout.addWidget(self.hand1_suit_combo, 1, 2, Qt.AlignLeft)

        self.hand1_rank_combo = QComboBox()
        self.hand1_rank_combo.addItems(self.ranks)
        self.hand1_rank_combo.setCurrentText("A")
        input_layout.addWidget(self.hand1_rank_combo, 1, 3, Qt.AlignLeft)

        # 第二张手牌
        input_layout.addWidget(QLabel("第二张牌:"), 1, 4, Qt.AlignLeft)
        self.hand2_suit_combo = QComboBox()
        self.hand2_suit_combo.addItems(list(self.suit_names.values()))
        self.hand2_suit_combo.setCurrentIndex(1)
        input_layout.addWidget(self.hand2_suit_combo, 1, 5, Qt.AlignLeft)

        self.hand2_rank_combo = QComboBox()
        self.hand2_rank_combo.addItems(self.ranks)
        self.hand2_rank_combo.setCurrentText("K")
        input_layout.addWidget(self.hand2_rank_combo, 1, 6, Qt.AlignLeft)

        # 公牌输入 - 翻牌 (3张)
        input_layout.addWidget(QLabel("翻牌 (3张):"), 2, 0, Qt.AlignLeft)

        # 翻牌1
        input_layout.addWidget(QLabel("第1张:"), 2, 1, Qt.AlignLeft)
        self.flop1_suit_combo = QComboBox()
        self.flop1_suit_combo.addItems(list(self.suit_names.values()))
        input_layout.addWidget(self.flop1_suit_combo, 2, 2, Qt.AlignLeft)

        self.flop1_rank_combo = QComboBox()
        self.flop1_rank_combo.addItems(self.ranks)
        self.flop1_rank_combo.setCurrentText("2")
        input_layout.addWidget(self.flop1_rank_combo, 2, 3, Qt.AlignLeft)

        # 翻牌2
        input_layout.addWidget(QLabel("第2张:"), 2, 4, Qt.AlignLeft)
        self.flop2_suit_combo = QComboBox()
        self.flop2_suit_combo.addItems(list(self.suit_names.values()))
        self.flop2_suit_combo.setCurrentIndex(1)
        input_layout.addWidget(self.flop2_suit_combo, 2, 5, Qt.AlignLeft)

        self.flop2_rank_combo = QComboBox()
        self.flop2_rank_combo.addItems(self.ranks)
        self.flop2_rank_combo.setCurrentText("3")
        input_layout.addWidget(self.flop2_rank_combo, 2, 6, Qt.AlignLeft)

        # 翻牌3
        input_layout.addWidget(QLabel("第3张:"), 2, 7, Qt.AlignLeft)
        self.flop3_suit_combo = QComboBox()
        self.flop3_suit_combo.addItems(list(self.suit_names.values()))
        self.flop3_suit_combo.setCurrentIndex(2)
        input_layout.addWidget(self.flop3_suit_combo, 2, 8, Qt.AlignLeft)

        self.flop3_rank_combo = QComboBox()
        self.flop3_rank_combo.addItems(self.ranks)
        self.flop3_rank_combo.setCurrentText("4")
        input_layout.addWidget(self.flop3_rank_combo, 2, 9, Qt.AlignLeft)

        # 公牌输入 - 转牌 (1张)
        input_layout.addWidget(QLabel("转牌 (1张):"), 3, 0, Qt.AlignLeft)

        input_layout.addWidget(QLabel("牌:"), 3, 1, Qt.AlignLeft)
        self.turn_suit_combo = QComboBox()
        self.turn_suit_combo.addItems(list(self.suit_names.values()))
        self.turn_suit_combo.setCurrentIndex(3)
        input_layout.addWidget(self.turn_suit_combo, 3, 2, Qt.AlignLeft)

        self.turn_rank_combo = QComboBox()
        self.turn_rank_combo.addItems(self.ranks)
        self.turn_rank_combo.setCurrentText("5")
        input_layout.addWidget(self.turn_rank_combo, 3, 3, Qt.AlignLeft)

        # 公牌输入 - 河牌 (1张)
        input_layout.addWidget(QLabel("河牌 (1张):"), 4, 0, Qt.AlignLeft)

        input_layout.addWidget(QLabel("牌:"), 4, 1, Qt.AlignLeft)
        self.river_suit_combo = QComboBox()
        self.river_suit_combo.addItems(list(self.suit_names.values()))
        input_layout.addWidget(self.river_suit_combo, 4, 2, Qt.AlignLeft)

        self.river_rank_combo = QComboBox()
        self.river_rank_combo.addItems(self.ranks)
        self.river_rank_combo.setCurrentText("6")
        input_layout.addWidget(self.river_rank_combo, 4, 3, Qt.AlignLeft)

        # 模拟精度
        input_layout.addWidget(QLabel("模拟精度:"), 5, 0, Qt.AlignLeft)
        self.precision_combo = QComboBox()
        self.precision_combo.addItems(["快速模式 (1,000次)", "平衡模式 (10,000次)", "精确模式 (100,000次)", "自定义次数"])
        self.precision_combo.setCurrentText("平衡模式 (10,000次)")
        self.precision_combo.currentTextChanged.connect(self.on_precision_change)
        input_layout.addWidget(self.precision_combo, 5, 1, Qt.AlignLeft)

        # 自定义次数输入框 (默认隐藏)
        self.custom_sim_entry = QLineEdit("10000")
        self.custom_sim_entry.hide()
        input_layout.addWidget(self.custom_sim_entry, 5, 2, Qt.AlignLeft)

        # 按钮
        button_layout = QHBoxLayout()
        self.calculate_button = QPushButton("计算胜率")
        self.calculate_button.clicked.connect(self.calculate_win_rate)
        button_layout.addWidget(self.calculate_button)

        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_inputs)
        button_layout.addWidget(self.reset_button)

        self.quit_button = QPushButton("退出")
        self.quit_button.clicked.connect(self.close)
        button_layout.addWidget(self.quit_button)

        input_layout.addLayout(button_layout, 6, 0, 1, 10)

        self.main_layout.addWidget(input_group)

    def on_precision_change(self, text):
        if text == "自定义次数":
            self.custom_sim_entry.show()
        else:
            self.custom_sim_entry.hide()

    def create_result_section(self):
        result_group = QGroupBox("计算结果")
        result_layout = QGridLayout()
        result_group.setLayout(result_layout)

        # 当前状态
        result_layout.addWidget(QLabel("当前状态:"), 0, 0, Qt.AlignLeft)
        self.status_label = QLabel("等待输入...")
        self.status_label.setStyleSheet("color: blue;")
        result_layout.addWidget(self.status_label, 0, 1, Qt.AlignLeft)

        # 胜率
        result_layout.addWidget(QLabel("胜率:"), 1, 0, Qt.AlignLeft)
        self.win_rate_label = QLabel("0.00%")
        font = QFont("SimHei", 12, QFont.Bold)
        self.win_rate_label.setFont(font)
        result_layout.addWidget(self.win_rate_label, 1, 1, Qt.AlignLeft)

        # 优势倍数
        result_layout.addWidget(QLabel("优势倍数:"), 2, 0, Qt.AlignLeft)
        self.advantage_label = QLabel("0.0x")
        result_layout.addWidget(self.advantage_label, 2, 1, Qt.AlignLeft)

        # 策略建议
        result_layout.addWidget(QLabel("策略建议:"), 3, 0, Qt.AlignTop | Qt.AlignLeft)
        self.strategy_label = QLabel("")
        self.strategy_label.setWordWrap(True)
        self.strategy_label.setMaximumWidth(400)
        result_layout.addWidget(self.strategy_label, 3, 1, Qt.AlignLeft)

        # 公牌显示
        result_layout.addWidget(QLabel("当前公牌:"), 4, 0, Qt.AlignLeft)
        self.community_cards_label = QLabel("无")
        result_layout.addWidget(self.community_cards_label, 4, 1, Qt.AlignLeft)

        # 模拟次数
        result_layout.addWidget(QLabel("模拟次数:"), 5, 0, Qt.AlignLeft)
        self.sim_count_label = QLabel("0")
        result_layout.addWidget(self.sim_count_label, 5, 1, Qt.AlignLeft)

        self.main_layout.addWidget(result_group)

    def create_progress_section(self):
        progress_group = QGroupBox("计算进度")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.progress_text_label = QLabel("就绪")
        self.progress_text_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_text_label)

        self.main_layout.addWidget(progress_group)

    def reset_inputs(self):
        self.num_players_combo.setCurrentText("2")

        # 重置手牌
        self.hand1_suit_combo.setCurrentIndex(0)
        self.hand1_rank_combo.setCurrentText("A")
        self.hand2_suit_combo.setCurrentIndex(1)
        self.hand2_rank_combo.setCurrentText("K")

        # 重置翻牌
        self.flop1_suit_combo.setCurrentIndex(0)
        self.flop1_rank_combo.setCurrentText("2")
        self.flop2_suit_combo.setCurrentIndex(1)
        self.flop2_rank_combo.setCurrentText("3")
        self.flop3_suit_combo.setCurrentIndex(2)
        self.flop3_rank_combo.setCurrentText("4")

        # 重置转牌
        self.turn_suit_combo.setCurrentIndex(3)
        self.turn_rank_combo.setCurrentText("5")

        # 重置河牌
        self.river_suit_combo.setCurrentIndex(0)
        self.river_rank_combo.setCurrentText("6")

        self.precision_combo.setCurrentText("平衡模式 (10,000次)")
        self.custom_sim_entry.hide()
        self.status_label.setText("等待输入...")
        self.win_rate_label.setText("0.00%")
        self.advantage_label.setText("0.0x")
        self.strategy_label.setText("")
        self.community_cards_label.setText("无")
        self.sim_count_label.setText("0")
        self.progress_bar.setValue(0)
        self.progress_text_label.setText("就绪")
        self.calculator = None
        self.is_calculating = False

    def set_simulations(self):
        precision = self.precision_combo.currentText()
        if precision == "快速模式 (1,000次)":
            self.simulations = 1000
        elif precision == "平衡模式 (10,000次)":
            self.simulations = 10000
        elif precision == "精确模式 (100,000次)":
            self.simulations = 100000
        elif precision == "自定义次数":
            try:
                custom = int(self.custom_sim_entry.text())
                if 100 <= custom <= 1000000:
                    self.simulations = custom
                else:
                    QMessageBox.critical(self, "错误", "自定义次数必须在100到1,000,000之间")
                    return False
            except ValueError:
                QMessageBox.critical(self, "错误", "请输入有效的数字")
                return False
        return True

    def get_suit_key(self, suit_name):
        # 从花色名称获取对应的键
        for key, name in self.suit_names.items():
            if name == suit_name:
                return key
        return 's'  # 默认返回黑桃

    def calculate_win_rate(self):
        logging.info("开始计算胜率")
        if self.is_calculating:
            QMessageBox.information(self, "提示", "计算已在进行中，请等待完成")
            logging.info("计算已在进行中，取消重复请求")
            return

        # 设置模拟次数
        if not self.set_simulations():
            return

        # 获取玩家数量
        try:
            num_players = int(self.num_players_combo.currentText())
            if not 2 <= num_players <= 10:
                QMessageBox.critical(self, "错误", "玩家数量必须在2到10之间")
                return
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的玩家数量")
            return

        # 构建手牌
        try:
            hand1_suit = self.get_suit_key(self.hand1_suit_combo.currentText())
            hand1_rank = self.hand1_rank_combo.currentText()
            hand1 = f"{hand1_rank}{hand1_suit}"

            hand2_suit = self.get_suit_key(self.hand2_suit_combo.currentText())
            hand2_rank = self.hand2_rank_combo.currentText()
            hand2 = f"{hand2_rank}{hand2_suit}"

            hand_input = [hand1, hand2]
        except Exception as e:
            QMessageBox.critical(self, "错误", f"手牌构建错误: {str(e)}")
            return

        # 创建计算器实例
        try:
            self.calculator = PokerWinRateCalculator(num_players, hand_input)
        except ValueError as e:
            QMessageBox.critical(self, "错误", f"手牌输入错误: {e}")
            return

        # 添加公牌
        try:
            stage = self.stage_combo.currentText()
            community_cards = []

            if stage in ["翻牌后", "转牌后", "河牌后"]:
                # 翻牌
                flop1_suit = self.get_suit_key(self.flop1_suit_combo.currentText())
                flop1_rank = self.flop1_rank_combo.currentText()
                flop1 = f"{flop1_rank}{flop1_suit}"

                flop2_suit = self.get_suit_key(self.flop2_suit_combo.currentText())
                flop2_rank = self.flop2_rank_combo.currentText()
                flop2 = f"{flop2_rank}{flop2_suit}"

                flop3_suit = self.get_suit_key(self.flop3_suit_combo.currentText())
                flop3_rank = self.flop3_rank_combo.currentText()
                flop3 = f"{flop3_rank}{flop3_suit}"

                community_cards.extend([flop1, flop2, flop3])

            if stage in ["转牌后", "河牌后"]:
                # 转牌
                turn_suit = self.get_suit_key(self.turn_suit_combo.currentText())
                turn_rank = self.turn_rank_combo.currentText()
                turn = f"{turn_rank}{turn_suit}"
                community_cards.append(turn)

            if stage == "河牌后":
                # 河牌
                river_suit = self.get_suit_key(self.river_suit_combo.currentText())
                river_rank = self.river_rank_combo.currentText()
                river = f"{river_rank}{river_suit}"
                community_cards.append(river)

            if community_cards:
                self.calculator.add_community_cards(community_cards)

        except ValueError as e:
            QMessageBox.critical(self, "错误", f"公牌输入错误: {e}")
            return

        # 更新状态
        self.status_label.setText("计算中...")
        self.is_calculating = True
        self.sim_count_label.setText(str(self.simulations))

        # 显示当前公牌和阶段
        stage = self.stage_combo.currentText()
        if hasattr(self.calculator, 'community_cards') and len(self.calculator.community_cards) > 0:
            self.community_cards_label.setText(f"{stage} - " + ", ".join(str(c) for c in self.calculator.community_cards))
        else:
            self.community_cards_label.setText(f"{stage} - 无")

        # 在新线程中执行计算
        threading.Thread(target=self.run_calculation).start()

    def update_progress(self, current, total):
        # 这个方法会在计算线程中被调用
        self.progress_updater.update(current, total)

    def on_progress_updated(self, current, total):
        # 这个方法会在主线程中被调用
        progress = (current / total) * 100
        self.progress_bar.setValue(int(progress))
        self.progress_text_label.setText(f"已完成 {current}/{total} 次模拟")

    def run_calculation(self):
        try:
            start_time = time.time()
            win_rate = self.calculator.calculate_win_rate(self.simulations, self.update_progress)
            elapsed_time = time.time() - start_time

            # 计算优势倍数
            avg_win_rate = 1 / self.calculator.num_players
            win_advantage = win_rate / avg_win_rate if avg_win_rate > 0 else 0
            logging.info(f"计算完成: 胜率={win_rate:.2%}, 优势倍数={win_advantage:.1f}x")

            # 生成策略建议
            if win_advantage >= 2.0:
                strategy = "强烈建议加注"
            elif win_advantage >= 1.5:
                strategy = "建议跟注"
            elif win_advantage >= 1.0:
                strategy = "谨慎跟注"
            else:
                strategy = "建议弃牌"
            logging.info(f"策略建议: {strategy}")

            # 使用QTimer.singleShot确保在主线程中更新UI
            logging.info("调度UI更新")
            # 使用functools.partial避免lambda作用域问题
            from functools import partial
            update_func = partial(self.update_results, win_rate, win_advantage, strategy, elapsed_time)
            QTimer.singleShot(0, update_func)

        except Exception as e:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "计算错误", f"计算过程中出错: {str(e)}"))
        finally:
            self.is_calculating = False
            QTimer.singleShot(0, lambda: self.status_label.setText("计算完成"))

    def update_results(self, win_rate, win_advantage, strategy, elapsed_time):
        logging.info(f"更新结果: 胜率={win_rate:.2%}, 优势倍数={win_advantage:.1f}x")
        # 确保在主线程中更新UI
        if QThread.currentThread() != QApplication.instance().thread():
            logging.info("不在主线程中，切换到主线程更新UI")
            QTimer.singleShot(0, lambda: self.update_results(win_rate, win_advantage, strategy, elapsed_time))
            return
        else:
            logging.info("在主线程中更新UI")

        # 更新UI元素
        self.win_rate_label.setText(f"{win_rate:.2%}")
        self.advantage_label.setText(f"{win_advantage:.1f}x")
        #self.strategy_label.setText(f"{strategy} (基于{self.calculator.num_players}名玩家的竞争环境)")
        self.strategy_label.setText(f"{strategy}")
        self.progress_text_label.setText(f"计算完成 (耗时: {elapsed_time:.2f} 秒)")

        # 强制更新UI
        self.win_rate_label.repaint()
        self.advantage_label.repaint()
        self.strategy_label.repaint()
        self.progress_text_label.repaint()
        QApplication.instance().processEvents()
        logging.info("UI更新完成")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PokerGUI()
    window.show()
    sys.exit(app.exec_())