# analyze_correct_score.py
#!/usr/bin/env python3
import json
from analysts.score_analyzer import ScoreProbabilityAnalyzer
from analysts.score_report_generator import ScoreReportGenerator

def main():
    print("🎯 ANÁLISE DE PLACAR CORRETO - BRASILEIRÃO")
    print("=" * 60)
    
    # Carrega dados históricos
    try:
        with open('brasileirao_collection_results.json', 'r', encoding='utf-8') as f:
            historical_data = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de dados não encontrado. Execute primeiro a coleta.")
        return
    
    # Inicializa analisador
    analyzer = ScoreProbabilityAnalyzer(historical_data)
    report_generator = ScoreReportGenerator(analyzer)
    
    # Gera relatório completo
    print("1. 📊 Calculando probabilidades de Poisson...")
    print("2. 🔍 Analisando placares históricos...")
    print("3. 🎯 Identificando value bets...")
    print("4. 📈 Gerando previsões...")
    print("5. 💡 Desenvolvendo estratégias...")
    
    score_report = report_generator.generate_complete_score_report()
    
    # Salva relatório
    with open('relatorio_placar_correto.json', 'w', encoding='utf-8') as f:
        json.dump(score_report, f, indent=2, ensure_ascii=False, default=str)
    
    # Gera CSVs
    report_generator.generate_score_csv_reports(score_report)
    
    # Exibe insights principais
    print("\n🎯 PRINCIPAIS INSIGHTS - PLACAR CORRETO")
    print("=" * 60)
    
    # Placares mais comuns
    common_scores = list(score_report['placares_mais_comuns'].items())[:5]
    print("📊 PLACARES MAIS COMUNS NO BRASILEIRÃO:")
    for i, (score, stats) in enumerate(common_scores, 1):
        print(f"   {i}. {score}: {stats['percentage']}% (Odds Justas: {stats['fair_odds']})")
    
    # Previsões para clássicos
    print("\n🔮 PREVISÕES PARA PRÓXIMOS CLÁSSICOS:")
    predictions = score_report['previsoes_jogos_futuros']
    for match, prediction in list(predictions.items())[:3]:
        top_score = list(prediction['top_5_placares'].items())[0]
        print(f"   • {match}: {top_score[0]} ({top_score[1]['probability']}% prob)")
    
    # Estratégias
    strategies = score_report['estrategias_placar_correto']
    print(f"\n💡 ESTRATÉGIAS RECOMENDADAS:")
    print(f"   • {strategies['estrategia_principal']['nome']}")
    print(f"   • {strategies['estrategia_value_bets']['nome']}")
    print(f"   • Foco em: {', '.join(list(strategies['placares_mais_frequentes'].keys())[:3])}")
    
    # Value bets simulados
    print(f"\n💰 VALUE BETS IDENTIFICADOS:")
    for bet in score_report['value_bets_simulados'][:2]:
        print(f"   • {bet['jogo']} - {bet['placar']}: EV {bet['value_esperado']}")
    
    # Estatísticas gerais
    meta = score_report['metadata']
    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    print(f"   • Jogos analisados: {meta['total_jogos_analisados']}")
    print(f"   • Média de gols/jogo: {meta['media_gols_por_jogo']}")
    print(f"   • Placares que cobrem 50% dos jogos: {len(common_scores)}")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISE DE PLACAR CORRETO CONCLUÍDA!")
    print("📁 Arquivos gerados:")
    print("   • relatorio_placar_correto.json")
    print("   • placares_mais_comuns.csv")
    print("   • perfis_placar_times.csv")
    print("   • previsoes_placares.csv")

if __name__ == "__main__":
    main()
