from math import isfinite

from flask import Flask, redirect, render_template, request, url_for
from calculadora import calcular_basal, calcular_gasto_treino

app = Flask(__name__)

# Tempos típicos assumidos pelo site, em minutos por dia, fora do treino.
# Cada par indica tempo em pé e tempo de caminhada, sem sobreposição.
ROTINAS_FORA_ACADEMIA = {
    'sedentario': (60, 15),
    'Leve': (300, 30),
    'Moderado': (240, 90),
    'Intensa': (360, 150),
}


@app.route('/')
def inicio():
    return render_template('inicio.html')


@app.route('/sobre')    
def sobre():
    return render_template('sobre.html')


@app.route('/calcular')
def calcular():
    return render_template('calcular.html')


@app.route('/prosseguir', methods=['GET', 'POST'])
def gastos_energeticos():
    if request.method == 'GET':
        return redirect(url_for('calcular'))

    if request.form.get('etapa') == 'basal':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            idade = int(request.form['idade'])
            sexo = request.form['gender']

            taxa_basal = calcular_basal(peso, altura, idade, sexo)
            if not isfinite(taxa_basal) or taxa_basal <= 0:
                raise ValueError('Informe dados válidos para estimar a taxa basal.')

            return render_template(
                'prosseguir.html',
                taxa_basal=taxa_basal,
                peso=peso,
                idade=idade,
            )

        except (ValueError, KeyError) as e:
            return render_template(
                'calcular.html',
                error=str(e),
            ), 400

    peso = None
    taxa_basal = None
    idade = request.form.get('idade', type=int)
    try:
        peso = float(request.form['peso'])
        taxa_basal = float(request.form['basal'])
        if not isfinite(taxa_basal) or taxa_basal <= 0:
            taxa_basal = None
            raise ValueError('Volte à primeira etapa para calcular uma taxa basal válida.')
        treinos = int(request.form['treinos'])
        descanso = float(request.form['descanso'])
        horas = float(request.form['horas'])
        rotina = ROTINAS_FORA_ACADEMIA.get(request.form.get('atividade_fora'))
        if rotina is None:
            raise ValueError('Selecione uma opção válida de atividade fora da academia.')

        gasto_academia = calcular_gasto_treino(peso, treinos, descanso, horas)

    except (ValueError, KeyError) as e:
        mensagem = str(e)
        if isinstance(e, KeyError):
            mensagem = f'O formulário não enviou o campo "{e.args[0]}". Abra Calcular e envie os dados novamente.'
        return render_template(
            'prosseguir.html', peso=peso, taxa_basal=taxa_basal, idade=idade, error=mensagem,
        ), 400

    minutos_em_pe, minutos_caminhando = rotina
    # Compêndio 2024: em pé (07040, 1,3 MET) e caminhada lenta (17152, 2,8 MET).
    # Desconta 1 MET e converte o tempo em horas para estimar apenas o adicional.
    atividade_fora = peso * (
        (1.3 - 1) * minutos_em_pe + (2.8 - 1) * minutos_caminhando
    ) / 60
    # Soma os mesmos números inteiros exibidos na tela.
    taxa_basal = round(taxa_basal)
    gasto_academia = round(gasto_academia)
    atividade_fora = round(atividade_fora)
    gasto_total = taxa_basal + gasto_academia + atividade_fora

    # Referência ilustrativa: 0,24 kg/semana × 7700 kcal/kg ÷ 7 dias.
    objetivos = None
    if idade is not None and idade >= 18:
        ajuste = round(0.24 * 7700 / 7)
        objetivos = {
            'ajuste': ajuste,
            'manutencao': gasto_total,
            'deficit': gasto_total - ajuste if gasto_total - ajuste >= 1200 else None,
            'ganho_massa': gasto_total + ajuste,
        }
    return render_template(
        'prosseguir.html',
        peso=peso,
        idade=idade,
        taxa_basal=taxa_basal,
        gasto_academia=gasto_academia,
        atividade_fora=atividade_fora,
        gasto_total=gasto_total,
        objetivos=objetivos,
    )



if __name__ == "__main__":
    app.run(debug=True)


