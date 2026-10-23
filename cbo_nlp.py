from pathlib import Path

import nltk
import pandas as pd
import unidecode
from nltk import tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_DADOS = "C:\\Users\\ECO\\Desktop\\ITI - Polarização\\Patentes\\dados_tratados.csv"

for recurso in ("stopwords", "rslp"):
    try:
        nltk.data.find(
            f"corpora/{recurso}" if recurso == "stopwords"
            else f"stemmers/{recurso}"
        )
    except LookupError:
        nltk.download(recurso, quiet=True)

df = pd.read_csv(CAMINHO_DADOS)
df["descricao"] = df["descricao"].fillna("").astype(str)
df["tarefa"] = df["tarefa"].fillna("").astype(str)

palavras_irrelevantes = set(
    nltk.corpus.stopwords.words("portuguese")
)
token_pontuacao = tokenize.WordPunctTokenizer()
stemmer = nltk.RSLPStemmer()


def processar_avaliacao(avaliacao: str) -> str:
    tokens = token_pontuacao.tokenize(str(avaliacao))

    tokens = [
        palavra for palavra in tokens
        if palavra.lower() not in palavras_irrelevantes
        and palavra.isalpha()
    ]

    tokens = [
        stemmer.stem(unidecode.unidecode(palavra.lower()))
        for palavra in tokens
    ]

    return " ".join(tokens)


df["tratamento_5"] = df["descricao"].apply(processar_avaliacao)

tfidf_1000 = TfidfVectorizer(
    lowercase=False,
    max_features=1000,
    ngram_range=(1, 2)
)

vetor_tfidf = tfidf_1000.fit_transform(df["tratamento_5"])

x_treino, x_teste, y_treino, y_teste = train_test_split(
    vetor_tfidf,
    df["tarefa"],
    random_state=4979
)

regressao_multinomial = LogisticRegression(max_iter=1000)
regressao_multinomial.fit(x_treino, y_treino)


def agradação_das_tarefas(descricao: str) -> pd.DataFrame:
    descricao_processada = processar_avaliacao(descricao)
    descricao_tfidf = tfidf_1000.transform([descricao_processada])

    previsao = regressao_multinomial.predict(descricao_tfidf)[0]
    probabilidades = regressao_multinomial.predict_proba(descricao_tfidf)[0]

    resultado = pd.DataFrame(
        {
            "ocupacao": regressao_multinomial.classes_,
            "probabilidade": probabilidades,
        }
    ).sort_values("probabilidade", ascending=False)

    print(f"Ocupação prevista: {previsao}")
    print(f"Confiança: {resultado.iloc[0]['probabilidade'] * 100:.2f}%")

    return resultado.reset_index(drop=True)