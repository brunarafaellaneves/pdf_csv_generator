# Para a execução deste sistema você precisa possuir as bibliotecas
# Pandas, fpdf e matplotlib instaladas no seu dispositivo.

# Após as bibliotecas necessárias estarem instaladas, 
# basta executar o código pelo prompt de comando para que o relatório seja gerado.

# Desenvolvedora: Bruna Rafaella de Oliveira Neves
# Projeto de Extensão: Sistemas da Informação Estácio

import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os


# Padronizando o nome das colunas para facilitar a análise através do código.
def padronizando_colunas(df):
    new_column_names = {
        "Carimbo de data/hora": "timestamp",
        "Qual é a sua faixa etária?": "faixa_etaria",
        "Você está inserido no mercado de trabalho atualmente?": "inserido_mercado_trabalho",
        "Como você se identifica racialmente?": "raca",
        "Você já sentiu que perdeu oportunidades de emprego ou sofreu discriminação direta no mercado de trabalho devido à sua etnia?": "experiencia_discriminacao_trabalho",
        "Você se considera bem informado e atualizado sobre as competências e habilidades exigidas no mercado de trabalho atualmente?": "possui_competencias_atualizadas",
        "Você sabe como buscar oportunidades de emprego e elaborar um currículo eficaz?": "sabe_buscar_oportunidades",
        "Você já ouviu falar sobre racismo estrutural?": "conhecimento_racismo_estrutural",
        "Qual é o seu nível de entendimento sobre racismo estrutural?": "nivel_entendimento_racismo_estrutural",
        "Você já se sentiu ou conhece alguém que tenha se sentido discriminado(a) racialmente?": "sentiu_conhece_discriminacao_racial",
        "Na sua opinião, quais são os principais exemplos de racismo estrutural que você observa no seu dia a dia? (Você pode escolher mais de uma opção)": "exemplos_racismo_estrutural",
        "Você acredita que o ambiente e a estrutura social em que uma pessoa cresce e a sociedade está inserida podem influenciar as oportunidades de emprego e a escolha de candidatos negros e pardos para cargos no mercado de trabalho?": "opiniao_influencia_estrutura_social",
    }

    df = df.rename(columns=new_column_names)
    return df


# Categorizando as raças em dois grupos: Pretos e Pardos (foco) vs Outros
def categorizando_raca(row):
    if row in ["Negro(a)", "Pardo(a)"]:
        return "Pretos e Pardos"
    else:
        return "Brancos e Outros"


# Função para formatar as respostas agrupadas no PDF
def formatar_agrupamento(df, categoria):
    formatted_str = ""
    contagem_ordenada = (
        df.groupby("grupo_racial")[categoria]
        .apply(lambda x: x.value_counts())
        .unstack(fill_value=0)
        .fillna(0)
        .sort_index(ascending=True)
    )

    for grupo, dados in contagem_ordenada.iterrows():
        formatted_str += f"- {grupo}\n"
        for resposta, contagem in dados.sort_values(ascending=False).items():
            formatted_str += f"  * {resposta}: {contagem}\n"
    return formatted_str


# Função para criar gráficos e salvar em arquivos temporários
def criar_grafico(df, coluna, titulo):
    plt.figure(figsize=(8, 6))
    conteudo = df[coluna].value_counts().sort_index()
    plt.bar(conteudo.index, conteudo.values, color="skyblue")
    plt.xlabel(coluna)
    plt.ylabel("Contagem")
    plt.title(titulo)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Criar arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp_file.name)
    plt.close()

    return temp_file.name


# Função para gerar o relatório em PDF
def gerar_pdf(relatorio, nome_arquivo="relatorio.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título do Relatório
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(
        0,
        10,
        "Relatório de Percepções e Experiências sobre Racismo Estrutural",
        ln=True,
        align="C",
    )

    # Linha em branco para separar o título da introdução
    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    # Introdução do relatório
    introducao = (
        "Este relatório apresenta uma análise dos dados coletados sobre a percepção "
        "e experiência de discriminação racial no mercado de trabalho. "
        "O objetivo é compreender a relação entre a identidade racial dos respondentes e suas "
        "experiências e opiniões sobre racismo estrutural e oportunidades de emprego.\n\n"
    )
    pdf.multi_cell(0, 10, introducao)

    # Seções do relatório
    for section in relatorio:
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, section[0], ln=True)
        pdf.set_font("Arial", size=12)

        if section[1] is not None:
            pdf.multi_cell(0, 10, section[1])

        # Adiciona gráfico se houver
        if section[2] is not None:
            grafico_path = criar_grafico(*section[2])
            pdf.image(grafico_path, x=10, w=180)
            # Linha em branco após a imagem para organizar
            pdf.ln(10)

            # Remover arquivo temporário
            os.remove(grafico_path)

    pdf.output(nome_arquivo)


def executando_analise(caminho_csv):
    df = pd.read_csv(caminho_csv)
    df = padronizando_colunas(df)

    # Criando uma nova coluna para facilitar a análise através da raça
    df["grupo_racial"] = df["raca"].apply(categorizando_raca)

    # Contagem de faixas etárias
    faixa_etaria_contagem = df["faixa_etaria"].value_counts()

    # Contagem de raças
    raca_contagem = df["grupo_racial"].value_counts()

    # Porcentagem de pessoas pretas e pardas no mercado de trabalho
    pretos_pardos_trabalho = (
        df[df["grupo_racial"] == "Pretos e Pardos"][
            "inserido_mercado_trabalho"
        ].value_counts(normalize=True)
        * 100
    )
    pretos_pardos_trabalho_str = pretos_pardos_trabalho.to_string()

    # Formatação das respostas
    racismo_structural_contagem_str = formatar_agrupamento(
        df, "conhecimento_racismo_estrutural"
    )
    nivel_entendimento_racial_str = formatar_agrupamento(
        df, "nivel_entendimento_racismo_estrutural"
    )
    discriminacao_racial_racial_str = formatar_agrupamento(
        df, "sentiu_conhece_discriminacao_racial"
    )
    influencia_estrutura_racial_str = formatar_agrupamento(
        df, "opiniao_influencia_estrutura_social"
    )

    # Gerando o conteúdo do relatório
    relatorio = [
        ("Faixas Etárias dos Respondentes:", faixa_etaria_contagem.to_string(), None),
        ("Contagem de Raça dos Participantes:", raca_contagem.to_string(), None),
        (
            "Porcentagem de Pretos e Pardos no Mercado de Trabalho:",
            pretos_pardos_trabalho_str,
            None,
        ),
        (
            "Conhecimento sobre Racismo Estrutural (Pretos e Pardos vs Brancos e Outros):",
            racismo_structural_contagem_str,
            None,
        ),
        (
            "Nível de Entendimento sobre Racismo Estrutural por Raça:",
            nivel_entendimento_racial_str,
            None,
        ),
        (
            "Sentimento de Discriminação Racial ou Conhecimento de Alguém que Tenha Sofrido:",
            discriminacao_racial_racial_str,
            None,
        ),
        (
            "Opinião sobre a Influência da Estrutura Social nas Oportunidades de Emprego:",
            influencia_estrutura_racial_str,
            None,
        ),
        (
            "Métricas de Experiência de Trabalho:",
            None,
            (
                df,
                "experiencia_discriminacao_trabalho",
                "Experiência de Discriminação no Mercado de Trabalho",
            ),
        ),
        (
            "Métricas de Competências:",
            None,
            (df, "possui_competencias_atualizadas", "Competências Atualizadas"),
        ),
        (
            "Métricas de Busca de Oportunidades:",
            None,
            (df, "sabe_buscar_oportunidades", "Busca de Oportunidades"),
        ),
    ]

    gerar_pdf(relatorio, "relatorio.pdf")


# Iniciando execução 
# (alterar caminho caso arquivo esteja com nome diferente ou haja erro na execução pelos espaços)
caminho_csv = "process_form_data.csv"
executando_analise(caminho_csv)

