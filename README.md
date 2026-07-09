# Controle de Estoque (V1)

Este é um sistema desenvolvido em **Python (Flask)** e **SQLite** para gerenciamento e rastreabilidade de produtos (notebooks, monitores, periféricos) por meio de etiquetas de patrimônio. 

O foco principal desta primeira versão foi desenvolver uma arquitetura funcional e performática.

---

## Funcionalidades da V1
* **Cadastro de Movimentações:** Registro de Entradas e Saídas com captura de Marca, Modelo, Categoria, Quantidade, Status e Número de Série.
* **Consulta Sob Demanda:** Painel inicial limpo para otimização de performance. A listagem de dados só ocorre mediante busca por etiqueta específica ou acionamento do botão de listagem completa.
* **Lógica de Saldo Consolidada:** Cálculo em tempo real do estoque líquido disponível utilizando queries matemáticas agregadas (`SUM` com `CASE WHEN`) direto no SQLite.

---

## Tecnologias Utilizadas
* **Backend:** Python + Flask
* **Banco de Dados:** SQLite3
* **Frontend:** HTML5 / CSS3

---

## Projeto em Andamento

**Estou realizando melhorias para em breve subir uma V2 do projeto.**

---

## Como Rodar o Projeto

1. Instale o Flask:
   ```bash
   pip install flask

2. Execute:
    python estoque.py

3. Abra o navegador:
    http://localhost:5000/