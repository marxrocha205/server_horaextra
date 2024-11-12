from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from datetime import datetime, timedelta
import locale

app = Flask(__name__)

# Definir a localidade para português
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

# Lista para armazenar os registros de horas
horas_extras = []

# Função para calcular a diferença de horas extras e arredondar para 2 casas decimais
def calcular_horas(horario):
    try:
        inicio, fim = horario.split(' - ')
        inicio_dt = datetime.strptime(inicio, '%H:%M')
        fim_dt = datetime.strptime(fim, '%H:%M')

        # Se o fim é antes do início (caso de horários noturnos que cruzam a meia-noite)
        if fim_dt < inicio_dt:
            fim_dt += timedelta(days=1)

        # Calcula a diferença em horas e arredonda para 2 casas decimais
        horas = round((fim_dt - inicio_dt).total_seconds() / 3600, 2)
        return horas
    except Exception as e:
        return 0  # Se houver algum erro de formato, retorna 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.json['data']
    horarios = request.json['horarios']

    manha = None
    noite = None

    for horario in horarios:
        if 'Manhã' in horario:
            manha = horario.replace('Manhã: ', '').strip()
        elif 'Noite' in horario:
            noite = horario.replace('Noite: ', '').strip()

    # Adicionar os horários processados à lista
    horas_extras.append({
        'data': data,
        'manha': manha,
        'noite': noite
    })

    return jsonify({'status': 'Horário registrado com sucesso!'})

@app.route('/relatorio')
def relatorio():
    if len(horas_extras) == 0:
        return jsonify({'status': 'Nenhum registro de horas encontrado!'})

    # Criar lista para adicionar informações adicionais
    dados_completos = []
    total_horas_extras = 0
    total_horas_fim_semana = 0
    dias_com_horas_extras = set()

    for registro in horas_extras:
        data = registro['data']
        dia_semana = datetime.strptime(data, '%Y-%m-%d').strftime('%A')

        # Calcular horas da manhã e da noite
        horas_manha = calcular_horas(registro['manha']) if registro['manha'] else 0
        horas_noite = calcular_horas(registro['noite']) if registro['noite'] else 0
        horas_totais = horas_manha + horas_noite

        # Acumular o total de horas extras
        total_horas_extras += horas_totais

        # Se for fim de semana, acumular as horas
        if dia_semana in ['sábado', 'domingo']:
            total_horas_fim_semana += horas_totais

        # Se houve horas extras no dia, adicionar o dia ao set
        if horas_totais > 0:
            dias_com_horas_extras.add(data)

        # Adicionar ao conjunto de dados
        dados_completos.append({
            'data': data,
            'dia_semana': dia_semana,  # Em português
            'horario_manha': registro['manha'],   # Incluindo o horário cadastrado
            'horario_noite': registro['noite'],   # Incluindo o horário cadastrado
            'horas_manha': horas_manha,
            'horas_noite': horas_noite,
            'horas_totais': round(horas_totais, 2)  # Arredondando horas totais
        })

    # Criar um DataFrame com os dados completos
    df = pd.DataFrame(dados_completos)

    # Adicionar uma linha com o total geral
    df_total = pd.DataFrame({
        'data': ['Total'],
        'dia_semana': [''],
        'horario_manha': [''],
        'horario_noite': [''],
        'horas_manha': [round(df['horas_manha'].sum(), 2)],
        'horas_noite': [round(df['horas_noite'].sum(), 2)],
        'horas_totais': [round(total_horas_extras, 2)]
    })

    df = pd.concat([df, df_total], ignore_index=True)

    # Criar o arquivo Excel
    relatorio_path = 'relatorio_horas_extras.xlsx'
    writer = pd.ExcelWriter(relatorio_path, engine='xlsxwriter')

    # Escrever o DataFrame na primeira planilha
    df.to_excel(writer, sheet_name='Horas Extras', index=False)

    # Adicionar os totais em uma segunda planilha
    resumo = pd.DataFrame({
        'Descrição': ['Total de horas extras', 'Horas extras aos finais de semana', 'Dias com horas extras'],
        'Valor': [round(total_horas_extras, 2), round(total_horas_fim_semana, 2), len(dias_com_horas_extras)]
    })

    resumo.to_excel(writer, sheet_name='Resumo', index=False)

    writer.close()

    # Enviar o arquivo Excel para download
    return send_file(relatorio_path, as_attachment=True, download_name='relatorio_horas_extras.xlsx')

if __name__ == '__main__':
    app.run(debug=True)
