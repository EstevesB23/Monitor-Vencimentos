# Monitor de Vencimentos

Automação Python que lê planilhas Excel de cobranças, identifica parcelas próximas do vencimento e envia alertas por e-mail automaticamente.

## Contexto

Equipes financeiras que gerenciam cobranças em planilhas Excel perdem tempo verificando manualmente quais parcelas vencem nos próximos dias — e eventualmente deixam passar alertas importantes. Este projeto automatiza essa verificação: roda diariamente via agendador, lê a planilha, filtra os vencimentos relevantes e envia um e-mail HTML formatado com o relatório, sem intervenção manual.

O projeto nasceu da observação de um processo repetitivo que consome tempo operacional e gera risco de falha humana. A automação elimina os dois.

## Decisões técnicas

**Por que pandas em vez de ler o Excel diretamente?**
O pandas normaliza automaticamente diferentes formatos de data (`dd/mm/aaaa` e `aaaa-mm-dd`), lida com células vazias sem quebrar e permite filtrar por múltiplos status em uma linha. Ler linha por linha com openpyxl puro exigiria muito mais código para o mesmo resultado.

**Por que smtplib nativo em vez de uma biblioteca de e-mail?**
Para um script de automação agendado, dependências extras são pontos de falha. O smtplib já vem com Python, não precisa de instalação e é suficiente para SMTP com TLS. Menos dependências = menos manutenção.

**Por que `.env` em vez de configuração no código?**
Credenciais de e-mail nunca devem estar no código-fonte. O `.env.example` documenta o que precisa ser configurado sem expor valores reais, e o `.gitignore` garante que o `.env` nunca sobe pro repositório.

## Como funciona

```
planilha.xlsx → pandas filtra vencimentos → smtplib envia e-mail HTML
                                          → salva relatorio_AAAA-MM-DD.csv
                                          → registra em monitor.log
```

O script aceita qualquer planilha Excel com as colunas `cliente`, `valor`, `vencimento` e `status`. Parcelas com status `pago`, `pagamento_dia` ou `cancelado` são ignoradas automaticamente. O parâmetro `--dias` define a janela de alerta (padrão: 3 dias).

## Instalação

```bash
git clone https://github.com/EstevesB23/Monitor-Vencimentos.git
cd Monitor-Vencimentos/monitor-vencimentos

python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / Mac

pip install -r requirements.txt
cp .env.example .env        # configure suas credenciais de e-mail
```

> **Gmail:** gere uma senha de app em [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — não use a senha da conta diretamente.

## Como usar

```bash
# Gera uma planilha de exemplo para testar
python gerar_exemplo.py

# Roda o monitor (alerta para vencimentos nos próximos 3 dias)
python monitor.py planilha_exemplo.xlsx

# Janela personalizada
python monitor.py planilha_exemplo.xlsx --dias 7

# Apenas gera o CSV, sem enviar e-mail
python monitor.py planilha_exemplo.xlsx --so-relatorio
```

## Formato da planilha

| cliente | valor | vencimento | status |
|---|---|---|---|
| João Silva | 350.00 | 15/04/2025 | pendente |
| Maria Lima | 800.00 | 10/04/2025 | atrasado |

Colunas extras são aceitas sem problema. Aceita datas em `dd/mm/aaaa` ou `aaaa-mm-dd`.

## Saídas geradas

- E-mail HTML com tabela formatada dos vencimentos encontrados
- Arquivo CSV (`relatorio_AAAA-MM-DD.csv`) salvo localmente
- Log (`monitor.log`) com registro de cada execução

## Automatizar a execução

**Windows — Agendador de Tarefas:**
```
python C:\caminho\monitor.py C:\caminho\planilha.xlsx
```
Configure para rodar diariamente no horário desejado.

**Linux / Mac — cron:**
```bash
crontab -e
# Executa todo dia às 8h
0 8 * * * /caminho/venv/bin/python /caminho/monitor.py /caminho/planilha.xlsx
```

## Stack

- Python 3.10+
- pandas + openpyxl — leitura e manipulação da planilha
- smtplib — envio de e-mail via SMTP (nativo do Python)
- python-dotenv — gerenciamento de variáveis de ambiente
