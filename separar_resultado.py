import csv
import re
from pathlib import Path


entrada = Path(__file__).with_name('patentes_categorizadas.csv')
saida = Path(__file__).with_name('patentes_categorizadas_separadas.csv')

categorias = {
    'manual': 'Manual',
    'rotineiro_manual': 'R. Manual',
    'rotineiro_cognitivo': 'R. Cognitiva',
    'abstrata': 'Abstrata',
}
nomes_categoria = {
    nome.casefold().replace('_', ' ')
    for nome in categorias
}
padrao_resultado = re.compile(
    r'\s*\d+\s+(Abstrata|R\. Manual|R\. Cognitiva|Manual)\s+'
    r'([0-9]+(?:\.[0-9]+)?)'
)

linhas_separadas = {categoria: [] for categoria in categorias}

with entrada.open('r', encoding='utf-8-sig', newline='') as arquivo_entrada:
    leitor = csv.DictReader(arquivo_entrada)
    campos = leitor.fieldnames or []
    campos_base = [
        campo for campo in campos
        if campo.casefold().replace('_', ' ') not in nomes_categoria
    ]
    campos_saida = campos_base + list(categorias)

    with saida.open('w', encoding='utf-8-sig', newline='') as arquivo_saida:
        escritor = csv.DictWriter(arquivo_saida, fieldnames=campos_saida)
        escritor.writeheader()

        for linha in leitor:
            resultado = linha.get('Resultado', '').strip()
            probabilidades = {}
            for rotulo, valor in padrao_resultado.findall(resultado):
                for nome_coluna, rotulo_categoria in categorias.items():
                    if rotulo == rotulo_categoria:
                        probabilidades[nome_coluna] = float(valor)
                        break

            categoria_predita = max(probabilidades, key=probabilidades.get) if probabilidades else None
            valores = {
                nome_coluna: int(nome_coluna == categoria_predita)
                for nome_coluna in categorias
            }
            linha = {
                campo: linha.get(campo, '')
                for campo in campos_base
            }
            linha.update(valores)
            escritor.writerow(linha)

            if categoria_predita is not None:
                linhas_separadas[categoria_predita].append(linha)

for categoria, linhas in linhas_separadas.items():
    arquivo_categoria = saida.with_name(f'patentes_{categoria}.csv')
    with arquivo_categoria.open('w', encoding='utf-8-sig', newline='') as arquivo_saida:
        escritor = csv.DictWriter(arquivo_saida, fieldnames=campos_base + list(categorias))
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f'{arquivo_categoria.name}: {len(linhas)} patentes')

print(f'Arquivo criado: {saida.name}')