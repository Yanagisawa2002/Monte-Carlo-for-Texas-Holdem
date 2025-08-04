import random
import time
from collections import Counter
from tqdm import tqdm

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.rank_value = self.get_rank_value()
        
    def get_rank_value(self):
        if self.rank == 'A':
            return 14
        elif self.rank == 'K':
            return 13
        elif self.rank == 'Q':
            return 12
        elif self.rank == 'J':
            return 11
        else:
            return int(self.rank)
            
    def __repr__(self):
        return f"{self.rank}{self.suit}"
        
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
        
    def __hash__(self):
        return hash((self.rank, self.suit))

class Deck:
    def __init__(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(self.cards)
        
    def remove_card(self, card):
        for i, c in enumerate(self.cards):
            if c.rank == card.rank and c.suit == card.suit:
                del self.cards[i]
                return True
        return False
        
    def draw(self, count=1):
        if count == 1:
            return self.cards.pop()
        return [self.cards.pop() for _ in range(count)]

class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards):
        # 确保我们只评估5张牌
        if len(cards) > 5:
            # 生成所有可能的5张牌组合并找出最佳组合
            from itertools import combinations
            best_score = (0,)
            for combo in combinations(cards, 5):
                score = HandEvaluator.evaluate_5_card_hand(list(combo))
                if score > best_score:
                    best_score = score
            return best_score
        return HandEvaluator.evaluate_5_card_hand(cards)
    
    @staticmethod
    def evaluate_5_card_hand(cards):
        # 按牌力排序
        sorted_cards = sorted(cards, key=lambda x: x.rank_value, reverse=True)
        ranks = [card.rank_value for card in sorted_cards]
        suits = [card.suit for card in sorted_cards]
        
        # 检查同花
        is_flush = len(set(suits)) == 1
        
        # 检查顺子
        unique_ranks = sorted(list(set(ranks)), reverse=True)
        is_straight = False
        straight_rank = 0
        
        # 处理A-2-3-4-5的特殊情况
        if unique_ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_rank = 5
        else:
            for i in range(len(unique_ranks) - 4):
                if unique_ranks[i] - unique_ranks[i+4] == 4:
                    is_straight = True
                    straight_rank = unique_ranks[i]
                    break
        
        # 皇家同花顺
        if is_flush and is_straight and straight_rank == 14:
            return (10, straight_rank)
            
        # 同花顺
        if is_flush and is_straight:
            return (9, straight_rank)
            
        # 四条
        rank_counts = Counter(ranks)
        for rank, count in rank_counts.items():
            if count == 4:
                kicker = max([r for r in ranks if r != rank])
                return (8, rank, kicker)
                
        # 葫芦
        if len(rank_counts) == 2:
            for rank, count in rank_counts.items():
                if count == 3:
                    pair_rank = [r for r in rank_counts if r != rank][0]
                    return (7, rank, pair_rank)
                elif count == 2:
                    three_rank = [r for r in rank_counts if r != rank][0]
                    return (7, three_rank, rank)
                    
        # 同花
        if is_flush:
            return (6, [c.rank_value for c in sorted_cards])
            
        # 顺子
        if is_straight:
            return (5, straight_rank)
            
        # 三条
        for rank, count in rank_counts.items():
            if count == 3:
                kickers = sorted([r for r in ranks if r != rank], reverse=True)[:2]
                return (4, rank, kickers)
                
        # 两对
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = max([r for r in ranks if r not in pairs])
            return (3, pairs[0], pairs[1], kicker)
            
        # 一对
        if len(pairs) == 1:
            kickers = sorted([r for r in ranks if r != pairs[0]], reverse=True)[:3]
            return (2, pairs[0], kickers)
            
        # 高牌
        return (1, [c.rank_value for c in sorted_cards])

class PokerWinRateCalculator:
    def __init__(self, num_players, my_cards):
        self.num_players = num_players
        self.my_cards = self.parse_cards(my_cards)
        self.community_cards = []
        
    def parse_cards(self, card_strings):
        # 解析卡牌字符串为Card对象列表
        cards = []
        seen_cards = set()
        for card_str in card_strings:
            card_str = card_str.strip()
            if len(card_str) == 2:
                rank = card_str[0]
                suit = card_str[1]
            elif len(card_str) == 3 and card_str[0:2] == '10':
                rank = '10'
                suit = card_str[2]
            else:
                raise ValueError(f"无效的卡牌格式: {card_str}。正确格式如: As, Kd, 10h")
            
            # 验证点数
            valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            if rank not in valid_ranks:
                raise ValueError(f"无效的点数: {rank}。有效点数: 2-10, J, Q, K, A")
                
            # 验证花色
            valid_suits = ['s', 'h', 'd', 'c', '♠', '♥', '♦', '♣']
            if suit not in valid_suits:
                raise ValueError(f"无效的花色: {suit}。使用s(黑桃), h(红桃), d(方块), c(梅花)")
                
            # 转换花色为符号
            suit_map = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
            if suit in suit_map:
                suit = suit_map[suit]
                
            # 检查重复卡牌
            card_key = (rank, suit)
            if card_key in seen_cards:
                raise ValueError(f"卡牌重复: {rank}{suit}")
            seen_cards.add(card_key)
                
            cards.append(Card(rank, suit))
        return cards

    def add_community_cards(self, community_cards):
        # 添加公牌并验证
        new_cards = self.parse_cards(community_cards)
        
        # 检查卡牌数量是否合理
        total = len(self.community_cards) + len(new_cards)
        if total > 5:
            raise ValueError(f"公牌总数不能超过5张，当前已有{len(self.community_cards)}张")
            
        # 检查重复卡牌
        all_cards = self.my_cards + self.community_cards
        for card in new_cards:
            if card in all_cards:
                raise ValueError(f"卡牌重复: {card}")
            all_cards.append(card)
            
        self.community_cards.extend(new_cards)
    
    def calculate_win_rate(self, simulations=10000, progress_callback=None):
        # Monte Carlo simulation to calculate win rate
        wins = 0
        ties = 0
        total_simulations = simulations
    
        # Check if there are enough community cards
        if len(self.community_cards) > 5:
            raise ValueError("Community cards cannot exceed 5")
    
        start_time = time.time()
        progress_bar = tqdm(range(simulations), desc="Simulation Progress", unit="sim", ncols=100)
    
        for i in progress_bar:
            # Create new deck and remove known cards
            deck = Deck()
            for card in self.my_cards + self.community_cards:
                deck.remove_card(card)
    
            # Deal hands to other players
            other_players = []
            for _ in range(self.num_players - 1):
                if len(deck.cards) < 2:
                    # Not enough cards, skip this simulation
                    total_simulations -= 1
                    continue
                player_hand = [deck.draw(), deck.draw()]
                other_players.append(player_hand)
    
            # Deal remaining community cards
            remaining_community = []
            needed = 5 - len(self.community_cards)
            if len(deck.cards) < needed:
                # Not enough cards, skip this simulation
                total_simulations -= 1
                continue
            for _ in range(needed):
                remaining_community.append(deck.draw())
    
            # Evaluate my hand
            my_full_hand = self.my_cards + self.community_cards + remaining_community
            my_score = HandEvaluator.evaluate_hand(my_full_hand)
    
            # Evaluate other players' hands
            other_scores = []
            for hand in other_players:
                full_hand = hand + self.community_cards + remaining_community
                other_scores.append(HandEvaluator.evaluate_hand(full_hand))
    
            # Compare results
            if all(my_score > score for score in other_scores):
                wins += 1
            elif any(my_score == score for score in other_scores):
                ties += 1
    
            # Update progress callback every 100 simulations
            if progress_callback and i % 100 == 0:
                progress_callback(i + 1, simulations)
    
            # Update progress bar info
            elapsed_time = time.time() - start_time
            iterations_done = i + 1
            if iterations_done > 0:
                avg_time_per_iter = elapsed_time / iterations_done
                remaining_iter = simulations - iterations_done
                eta_seconds = remaining_iter * avg_time_per_iter
    
                # Format ETA time
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
                progress_bar.set_postfix_str(f"Win Rate: {wins/iterations_done:.2%}, ETA: {eta_str}")
    
        # Final progress update
        if progress_callback:
            progress_callback(simulations, simulations)
    
        if total_simulations == 0:
            return 0
    
        # Calculate win rate, counting ties as half a win
        win_rate = (wins + ties / 2) / total_simulations
        return win_rate

if __name__ == "__main__":
    print("=" * 40)
    print("说明: 输入卡牌时使用点数+花色的格式，例如: As(黑桃A), Kd(方块K)")
    print("花色: s=黑桃♠, h=红桃♥, d=方块♦, c=梅花♣")
    print("点数: 2-10, J, Q, K, A")
    print("功能说明: 支持分阶段计算胜率(翻牌前/翻牌后/转牌后/河牌后)，并提供胜率优势倍数和策略建议")
    print("=" * 40)
    try:
        # 获取玩家数量
        while True:
            num_players_input = input("请输入玩家总数（包括您自己，2-10人）: ")
            try:
                num_players = int(num_players_input)
                if 2 <= num_players <= 10:
                    break
                print("玩家数量必须在2到10之间")
            except ValueError:
                print("请输入有效的数字")
        
        # 获取用户手牌
        while True:
            my_cards_input = input("请输入您的手牌（例如: As Kd）: ").strip().split()
            if len(my_cards_input) == 2:
                try:
                    # 检查是否有重复卡牌
                    if my_cards_input[0] == my_cards_input[1]:
                        raise ValueError("手牌中包含重复卡牌")
                    calculator = PokerWinRateCalculator(num_players, my_cards_input)
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            else:
                print("请输入两张手牌，用空格分隔")
        
        # 选择模拟精度
        print("\n请选择模拟精度级别:")
        print("1. 快速模式 (1,000次模拟) - 最快速度")
        print("2. 平衡模式 (10,000次模拟) - 默认选项")
        print("3. 精确模式 (100,000次模拟) - 最高精度")
        print("4. 自定义次数")
        
        while True:
            precision_choice = input("请输入选项 (1-4): ")
            if precision_choice == '1':
                simulations = 1000
                break
            elif precision_choice == '2':
                simulations = 10000
                break
            elif precision_choice == '3':
                simulations = 100000
                break
            elif precision_choice == '4':
                try:
                    simulations = int(input("请输入自定义模拟次数 (100-1,000,000): "))
                    if 100 <= simulations <= 1000000:
                        break
                    print("请输入100到1,000,000之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("请输入1-4之间的选项")
        
        # 初始胜率（翻牌前）
        print("\n--- 翻牌前状态 ---")
        win_rate = calculator.calculate_win_rate(simulations)
        print(f"当前胜率: {win_rate:.2%} (模拟次数: {simulations})")
        
        # 翻牌阶段（3张公牌）
        while True:
            flop_input = input("请输入翻牌的3张公牌（例如: 2s 3h 5d）: ").strip().split()
            if len(flop_input) == 3:
                try:
                    calculator.add_community_cards(flop_input)
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            else:
                print("请输入3张翻牌公牌，用空格分隔")
        
        print("\n--- 翻牌后状态 ---")
        print(f"当前公牌: {', '.join(str(c) for c in calculator.community_cards)}")
        win_rate = calculator.calculate_win_rate(simulations)
        print(f"当前胜率: {win_rate:.2%} (模拟次数: {simulations})")
        
        # 转牌阶段（1张公牌）
        while True:
            turn_input = input("请输入转牌的1张公牌（例如: 7c）: ").strip().split()
            if len(turn_input) == 1:
                try:
                    calculator.add_community_cards(turn_input)
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            else:
                print("请输入1张转牌公牌")
        
        print("\n--- 转牌后状态 ---")
        print(f"当前公牌: {', '.join(str(c) for c in calculator.community_cards)}")
        win_rate = calculator.calculate_win_rate(simulations)
        print(f"当前胜率: {win_rate:.2%} (模拟次数: {simulations})")
        
        # 河牌阶段（1张公牌）
        while True:
            river_input = input("请输入河牌的1张公牌（例如: Jh）: ").strip().split()
            if len(river_input) == 1:
                try:
                    calculator.add_community_cards(river_input)
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            else:
                print("请输入1张河牌公牌")
        
        print("\n--- 河牌后状态 ---")
        print(f"当前公牌: {', '.join(str(c) for c in calculator.community_cards)}")
        win_rate = calculator.calculate_win_rate(simulations)
        try:
            # 计算胜率优势倍数（当前胜率 / 平均胜率）
            avg_win_rate = 1 / calculator.num_players
            win_advantage = win_rate / avg_win_rate if avg_win_rate > 0 else 0
            
            # 根据优势倍数生成策略建议
            if win_advantage >= 2.0:
                strategy = "强烈建议加注"
            elif win_advantage >= 1.5:
                strategy = "建议跟注"
            elif win_advantage >= 1.0:
                strategy = "谨慎跟注"
            else:
                strategy = "建议弃牌"
            
            print(f"最终结果: 胜率 {win_rate:.2%}, 优势倍数 {win_advantage:.1f}x (模拟次数: {simulations})\n")
            print(f"策略建议: {strategy} (基于{calculator.num_players}名玩家的竞争环境)\n")
            print("优势倍数说明: >1.0x表示高于平均水平，数值越大优势越明显；<1.0x表示低于平均水平\n")
        except Exception as e:
            print(f"结果计算出错: {str(e)}")
            print(f"最终胜率: {win_rate:.2%} (模拟次数: {simulations})\n")
        
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        print("\n感谢使用德州扑克胜率计算器")
