# analysts/score_report_generator.py
import json
import pandas as pd
from datetime import datetime

class ScoreReportGenerator:
    def __init__(self, score_analyzer):
        self.analyzer = score_analyzer
    
    def generate_complete_score_report(self) -> Dict:
        """Gera relatório completo de placar correto"""
        print("🎯 Analisando probabilidades de placar correto...")
        
        report = {
            'metadata': {
                'gerado_em': datetime.now().isoformat(),
                'total_jogos_analisados': len(self.analyzer.all_matches),
                'media_gols_por_jogo': round(self.analyzer.df_all['total_goals'].mean(), 2)
            },
            'placares_mais_comuns': self.analyzer.analyze_common_scores(),
            'perfis_times': self.analyzer.get_team_score_profiles(),
            'previsoes_jogos_futuros': self._generate_future_predictions(),
            'estrategias_placar_correto': self._generate_score_strategies(),
            'value_bets_simulados': self._simulate_value_bets()
        }
        
        return report
    
    def _generate_future_predictions(self) -> Dict:
        """Gera previsões para jogos futuros baseados em confrontos similares"""
        # Times mais comuns do Brasileirão
        common_matches = [
            {'home': 'Flamengo', 'away': 'Palmeiras', 'description': 'Clássico nacional'},
            {'home': 'São Paulo', 'away': 'Corinthians', 'description': 'Majestoso'},
            {'home': 'Grêmio', 'away': 'Internacional', 'description': 'Grenal'},
            {'home': 'Flamengo', 'away': 'Fluminense', 'description': 'Fla-Flu'},
            {'home': 'Atlético-MG', 'away': 'Cruzeiro', 'description': 'Clássico Mineiro'}
        ]
        
        predictions = {}
        
        for match in common_matches:
            home, away = match['home'], match['away']
            probabilities = self.analyzer.calculate_score_probabilities(home, away)
            
            if probabilities:
                predictions[f"{home} vs {away}"] = {
                    'description': match['description'],
                    'top_5_placares': dict(list(probabilities.items())[:5]),
                    'placar_mais_provavel': list(probabilities.items())[0],
                    'expectativa_gols': {
                        'home': list(probabilities.values())[0]['expected_home_goals'],
                        'away': list(probabilities.values())[0]['expected_away_goals']
                    }
                }
        
        return predictions
    
    def _generate_score_strategies(self) -> Dict:
        """Gera estratégias específicas para apostas em placar correto"""
        strategies = {
            'placares_mais_frequentes': {
                '1x0': 'Mais comum no futebol brasileiro (8-12% dos jogos)',
                '1x1': 'Empate comum, bom para odds médias',
                '2x1': 'Vitória com gol de diferença, frequente',
                '2x0': 'Vitória convincente de times fortes em casa',
                '0x0': 'Mais comum em jogos de times defensivos'
            },
            'estrategia_principal': {
                'nome': 'Foco nos Top 5 Placares',
                'descricao': 'Concentrar em 4-5 placares que cobrem 30-40% das probabilidades',
                'implementacao': 'Selecionar placares que somem 35%+ de probabilidade total',
                'vantagem': 'Maior cobertura com menos apostas'
            },
            'estrategia_value_bets': {
                'nome': 'Busca por Odds Infladas',
                'descricao': 'Identificar placares com odds acima das probabilidades reais',
                'alvo': 'Placares com EV > 10%',
                'exemplo': 'Odds 8.00 para placar com 15% de probabilidade real'
            },
            'estrategia_especifica_times': {
                'times_offensivos': 'Focar em placares altos (2-1, 3-1, 2-2)',
                'times_defensivos': 'Placares baixos (1-0, 0-0, 1-1)',
                'clássicos': 'Placares equilibrados (1-1, 2-1, 1-2)'
            }
        }
        
        return strategies
    
    def _simulate_value_bets(self) -> List[Dict]:
        """Simula value bets para demonstração"""
        value_bets = []
        
        # Exemplos de value bets simulados
        example_bets = [
            {
                'jogo': 'Flamengo vs Vasco',
                'placar': '2-0',
                'probabilidade_real': 12.5,
                'odds_disponiveis': 7.50,
                'fair_odds': 8.00,
                'value_esperado': '+6.7%',
                'confianca': 'Alta'
            },
            {
                'jogo': 'São Paulo vs Corinthians', 
                'placar': '1-1',
                'probabilidade_real': 15.2,
                'odds_disponiveis': 6.00,
                'fair_odds': 6.58,
                'value_esperado': '+9.7%',
                'confianca': 'Média'
            },
            {
                'jogo': 'Palmeiras vs Fortaleza',
                'placar': '1-0',
                'probabilidade_real': 11.8,
                'odds_disponiveis': 8.50,
                'fair_odds': 8.47,
                'value_esperado': '+0.4%',
                'confianca': 'Baixa'
            }
        ]
        
        return example_bets
    
    def generate_score_csv_reports(self, report: Dict):
        """Gera relatórios em CSV para análise detalhada"""
        
        # CSV de placares mais comuns
        common_scores_data = []
        for score, stats in report['placares_mais_comuns'].items():
            common_scores_data.append({
                'placar': score,
                'frequencia': stats['frequency'],
                'percentual': stats['percentage'],
                'odds_justas': stats['fair_odds']
            })
        
        pd.DataFrame(common_scores_data).to_csv('placares_mais_comuns.csv', index=False, encoding='utf-8')
        
        # CSV de perfis dos times
        teams_profile_data = []
        for team, profile in report['perfis_times'].items():
            top_score = list(profile['top_scores'].items())[0] if profile['top_scores'] else ('0-0', 0)
            teams_profile_data.append({
                'time': team,
                'placar_mais_comum': top_score[0],
                'frequencia_placar': top_score[1],
                'media_gols_casa': profile['avg_goals_scored_home'],
                'media_gols_fora': profile['avg_goals_scored_away'],
                'media_gols_sofridos_casa': profile['avg_goals_conceded_home'],
                'media_gols_sofridos_fora': profile['avg_goals_conceded_away'],
                'clean_sheets_casa': round(profile['clean_sheets_home'], 1),
                'clean_sheets_fora': round(profile['clean_sheets_away'], 1)
            })
        
        pd.DataFrame(teams_profile_data).to_csv('perfis_placar_times.csv', index=False, encoding='utf-8')
        
        # CSV de previsões
        predictions_data = []
        for match, prediction in report['previsoes_jogos_futuros'].items():
            for score, prob in prediction['top_5_placares'].items():
                predictions_data.append({
                    'jogo': match,
                    'placar': score,
                    'probabilidade': prob['probability'],
                    'odds_justas': prob['fair_odds'],
                    'expectativa_gols_casa': prediction['expectativa_gols']['home'],
                    'expectativa_gols_fora': prediction['expectativa_gols']['away']
                })
        
        pd.DataFrame(predictions_data).to_csv('previsoes_placares.csv', index=False, encoding='utf-8')
        
        print("✅ CSVs para placar correto gerados:")
        print("   - placares_mais_comuns.csv")
        print("   - perfis_placar_times.csv")
        print("   - previsoes_placares.csv")
