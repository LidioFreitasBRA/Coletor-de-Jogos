# tools/score_betting_simulator.py
import pandas as pd
import numpy as np

class ScoreBettingSimulator:
    def __init__(self, score_analyzer):
        self.analyzer = score_analyzer
    
    def simulate_betting_strategy(self, initial_bankroll: float = 1000, bets_per_round: int = 5):
        """Simula estratégia de apostas em placar correto"""
        bankroll = initial_bankroll
        history = []
        
        # Simula 100 rodadas de apostas
        for round_num in range(100):
            # Seleciona jogos aleatórios para simulação
            available_teams = list(self.analyzer.team_stats.keys())
            np.random.shuffle(available_teams)
            
            round_profit = 0
            round_bets = []
            
            for i in range(0, min(bets_per_round * 2, len(available_teams)), 2):
                if i + 1 >= len(available_teams):
                    break
                    
                home_team = available_teams[i]
                away_team = available_teams[i + 1]
                
                # Calcula probabilidades
                probabilities = self.analyzer.calculate_score_probabilities(home_team, away_team)
                if not probabilities:
                    continue
                
                # Seleciona o placar mais provável
                most_likely_score = list(probabilities.items())[0]
                probability = most_likely_score[1]['probability'] / 100
                fair_odds = most_likely_score[1]['fair_odds']
                
                # Simula odds disponíveis (com margem da casa)
                available_odds = fair_odds * 0.92  # 8% de margem
                
                # Calcula stake usando critério de Kelly
                kelly_fraction = (probability * available_odds - 1) / (available_odds - 1)
                stake = max(10, min(100, bankroll * 0.02 * max(0, kelly_fraction)))
                
                # Simula resultado (baseado na probabilidade real)
                wins = np.random.random() < probability
                profit = stake * (available_odds - 1) if wins else -stake
                
                round_profit += profit
                round_bets.append({
                    'match': f"{home_team} vs {away_team}",
                    'score': most_likely_score[0],
                    'probability': probability * 100,
                    'odds': available_odds,
                    'stake': stake,
                    'result': 'WIN' if wins else 'LOSS',
                    'profit': profit
                })
            
            bankroll += round_profit
            history.append({
                'round': round_num + 1,
                'bankroll': bankroll,
                'profit': round_profit,
                'bets_placed': len(round_bets),
                'winning_bets': len([b for b in round_bets if b['result'] == 'WIN'])
            })
        
        return {
            'final_bankroll': bankroll,
            'total_return': ((bankroll - initial_bankroll) / initial_bankroll) * 100,
            'history': history
        }
