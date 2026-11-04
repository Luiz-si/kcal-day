import math


def calcular_basal(peso, altura, idade, sexo):
    """Gasto energético de repouso: Mifflin–St Jeor (1990).

    Fonte: https://pubmed.ncbi.nlm.nih.gov/2305711/
    """
    base = (10 * peso) + (6.25 * altura) - (5 * idade)

    if sexo == "male":
        return base + 5
    elif sexo == "female":
        return base - 161
    else:
        raise ValueError("Selecione uma opção de sexo válida.")


def calcular_gasto_treino(peso, treinos, descanso, horas):
    """Retorna o adicional médio de musculação em kcal/dia.

    Peso em kg, treinos por semana, descanso em minutos e sessão em horas.
    Usa 3,5 METs na execução (Compêndio 2024, código 02054) e assume
    repouso de referência nas pausas, com 30 segundos de execução por série.
    """
    valores = (peso, treinos, descanso, horas)

    if not all(math.isfinite(v) for v in valores):
        raise ValueError("Informe apenas números finitos.")

    if peso <= 0:
        raise ValueError("O peso precisa ser maior que zero.")

    if not 0 <= treinos <= 7 or int(treinos) != treinos:
        raise ValueError("Informe de 0 a 7 treinos por semana.")

    if descanso < 0 or not 0 <= horas <= 24:
        raise ValueError("Descanso ou duração inválidos.")

    if treinos > 0 and horas == 0:
        raise ValueError("Informe a duração do treino.")

    minutos_por_serie = 0.5
    horas_ativas = horas * (minutos_por_serie / (minutos_por_serie + descanso))
    # 1 MET equivale a aproximadamente 1 kcal/kg/h de repouso de referência.
    # A diferença em METs é convertida em kcal antes de entrar no total diário.
    return (3.5 - 1) * peso * horas_ativas * treinos / 7
