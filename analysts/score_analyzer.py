# analysts/score_analyzer.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
from scipy.stats import poisson
import math

class ScoreProbabilityAnalyzer:
    def __init__(self, matches_data: Dict):
        self.matches_2023 = matches_data.get('2023', [])
        self.matches_2024 = matches_data.get('2024', [])
        self.all_matches = self.matches_2023 + self.matches_2024
        self.df_all = pd.DataFrame(self.all_matches)
        
        # Estatísticas por time
        self.team_stats = self._calculate_team_stats()
    
    def _calculate_team_stats(self) -> Dict:
        """Calcula estatísticas ofensivas e defensivas de cada time"""
        team_stats = {}
        
        all_teams = set(self.df_all['home_team'].unique()) | set(self.df_all['away_team'].unique())
        
        for team in all_teams:
            # Jogos como mandante
            home_games = self.df_all[self.df_all['home_team'] == team]
            away_games = self.df_all[self.df_all['away_team'] == team]
            
            # Estatísticas ofensivas
            goals_for_home = home_games['home_score'].sum()
            goals_for_away = away_games['away_score'].sum()
            goals_against_home = home_games['away_score'].sum()
            goals_against_away = away_games['home_score'].sum()
            
            total_games = len(home_games) + len(away_games)
            
            if total_games == 0:
                continue
            
            # Médias de gols
            avg_goals_for_home = goals_for_home / len(home_games) if len(home_games) > 0 else 0
            avg_goals_for_away = goals_for_away / len(away_games) if len(away_games) > 0 else 0
            avg_goals_against_home = goals_against_home / len(home_games) if len(home_games) > 0 else 0
            avg_goals_against_away = goals_against_away / len(away_games) if len(away_games) > 0 else 0
            
            # Força ofensiva e defensiva
            league_avg_home_goals = self.df_all['home_score'].mean()
            league_avg_away_goals = self.df_all['away_score'].mean()
            
            attack_strength_home = avg_goals_for_home / league_avg_home_goals if league_avg_home_goals > 0 else 1
            attack_strength_away = avg_goals_for_away / league_avg_away_goals if league_avg_away_goals > 0 else 1
            defense_strength_home = avg_goals_against_home / league_avg_away_goals if league_avg_away_goals > 0 else 1
            defense_strength_away = avg_goals_against_away / league_avg_home_goals if league_avg_home_goals > 0 else 1
            
            team_stats[team] = {
                'attack_home': attack_strength_home,
                'attack_away': attack_strength_away,
                'defense_home': defense_strength_home,
                'defense_away': defense_strength_away,
                'avg_goals_for_home': avg_goals_for_home,
                'avg_goals_for_away': avg_goals_for_away,
                'avg_goals_against_home': avg_goals_against_home,
                'avg_goals_against_away': avg_goals_against_away,
                'total_games': total_games
            }
        
        return team_stats
    
    def calculate_score_probabilities(self, home_team: str, away_team: str) -> Dict:
        """Calcula probabilidades para todos os placares possíveis"""
        if home_team not in self.team_stats or away_team not in self.team_stats:
            return {}
        
        # Calcula expectativa de gols usando o modelo de Poisson
        home_attack = self.team_stats[home_team]['attack_home']
        away_defense = self.team_stats[away_team]['defense_away']
        away_attack = self.team_stats[away_team]['attack_away'] 
        home_defense = self.team_stats[home_team]['defense_home']
        
        league_avg_home = self.df_all['home_score'].mean()
        league_avg_away = self.df_all['away_score'].mean()
        
        # Expectativa de gols para cada time
        expected_home_goals = home_attack * away_defense * league_avg_home
        expected_away_goals = away_attack * home_defense * league_avg_away
        
        # Ajusta para valores realistas
        expected_home_goals = max(0.1, min(4.0, expected_home_goals))
        expected_away_goals = max(0.1, min(4.0, expected_away_goals))
        
        # Calcula probabilidades usando distribuição de Poisson
        score_probabilities = {}
        total_probability = 0
        
        # Analisa placares de 0-0 até 5-5
        for home_goals in range(0, 6):
            for away_goals in range(0, 6):
                # Probabilidade usando Poisson
                prob_home = poisson.pmf(home_goals, expected_home_goals)
                prob_away = poisson.pmf(away_goals, expected_away_goals)
                joint_probability = prob_home * prob_away
                
                score = f"{home_goals}-{away_goals}"
                score_probabilities[score] = {
                    'probability': round(joint_probability * 100, 3),
                    'fair_odds': round(1 / joint_probability, 2) if joint_probability > 0 else 999,
                    'expected_home_goals': round(expected_home_goals, 2),
                    'expected_away_goals': round(expected_away_goals, 2)
                }
                
                total_probability += joint_probability
        
        # Normaliza as probabilidades para somar 100%
        normalization_factor = 1 / total_probability
        for score in score_probabilities:
            score_probabilities[score]['probability'] = round(
                score_probabilities[score]['probability'] * normalization_factor, 3
            )
            if score_probabilities[score]['fair_odds'] < 999:
                score_probabilities[score]['fair_odds'] = round(
                    1 / (score_probabilities[score]['probability'] / 100), 2
                )
        
        return dict(sorted(
            score_probabilities.items(), 
            key=lambda x: x[1]['probability'], 
            reverse=True
        ))
    
    def find_value_bets(self, home_team: str, away_team: str, available_odds: Dict) -> List[Dict]:
        """Identifica value bets comparando probabilidades com odds disponíveis"""
        probabilities = self.calculate_score_probabilities(home_team, away_team)
        value_bets = []
        
        for score, prob_data in probabilities.items():
            if score in available_odds:
                fair_odds = prob_data['fair_odds']
                available_odd = available_odds[score]
                
                # Calcula valor esperado
                expected_value = (fair_odds / available_odd - 1) * 100
                
                if expected_value > 5:  # Value bet se EV > 5%
                    value_bets.append({
                        'score': score,
                        'probability': prob_data['probability'],
                        'fair_odds': fair_odds,
                        'available_odds': available_odd,
                        'expected_value': round(expected_value, 1),
                        'confidence': 'Alta' if expected_value > 15 else 'Média'
                    })
        
        return sorted(value_bets, key=lambda x: x['expected_value'], reverse=True)
    
    def analyze_common_scores(self) -> Dict:
        """Analisa os placares mais comuns no campeonato"""
        # Conta frequência de placares reais
        score_counts = {}
        total_matches = len(self.df_all)
        
        for _, match in self.df_all.iterrows():
            score = f"{int(match['home_score'])}-{int(match['away_score'])}"
            score_counts[score] = score_counts.get(score, 0) + 1
        
        # Calcula porcentagens
        common_scores = {}
        for score, count in score_counts.items():
            percentage = round((count / total_matches) * 100, 2)
            common_scores[score] = {
                'frequency': count,
                'percentage': percentage,
                'fair_odds': round(100 / percentage, 2) if percentage > 0 else 999
            }
        
        return dict(sorted(
            common_scores.items(), 
            key=lambda x: x[1]['percentage'], 
            reverse=True
        ))
    
    def get_team_score_profiles(self) -> Dict:
        """Analisa perfis de placar por time"""
        team_profiles = {}
        
        for team in self.team_stats.keys():
            team_matches = self.df_all[
                (self.df_all['home_team'] == team) | (self.df_all['away_team'] == team)
            ]
            
            # Placaes mais frequentes envolvendo o time
            score_frequencies = {}
            for _, match in team_matches.iterrows():
                if match['home_team'] == team:
                    score = f"{int(match['home_score'])}-{int(match['away_score'])}"
                else:
                    score = f"{int(match['away_score'])}-{int(match['home_score'])}"
                
                score_frequencies[score] = score_frequencies.get(score, 0) + 1
            
            # Top 5 placares mais comuns
            top_scores = dict(sorted(
                score_frequencies.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5])
            
            # Estatísticas de gols
            home_goals = team_matches[team_matches['home_team'] == team]['home_score'].mean()
            away_goals = team_matches[team_matches['away_team'] == team]['away_score'].mean()
            goals_conceded_home = team_matches[team_matches['home_team'] == team]['away_score'].mean()
            goals_conceded_away = team_matches[team_matches['away_team'] == team]['home_score'].mean()
            
            team_profiles[team] = {
                'top_scores': top_scores,
                'avg_goals_scored_home': round(home_goals, 2),
                'avg_goals_scored_away': round(away_goals, 2),
                'avg_goals_conceded_home': round(goals_conceded_home, 2),
                'avg_goals_conceded_away': round(goals_conceded_away, 2),
                'clean_sheets_home': len(team_matches[(team_matches['home_team'] == team) & 
                                                    (team_matches['away_score'] == 0)]) / len(team_matches[team_matches['home_team'] == team]) * 100,
                'clean_sheets_away': len(team_matches[(team_matches['away_team'] == team) & 
                                                    (team_matches['home_score'] == 0)]) / len(team_matches[team_matches['away_team'] == team]) * 100
            }
        
        return team_profiles
