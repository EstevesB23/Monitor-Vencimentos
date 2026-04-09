[README.md](https://github.com/user-attachments/files/26606474/README.md)
# 📅 Monitor de Vencimentos

Automação em Python que lê uma planilha Excel com parcelas/cobranças, identifica os vencimentos próximos e envia alertas por e-mail automaticamente.

---

## 🛠️ Tecnologias

- **Python 3.10+**
- **pandas** — leitura e manipulação da planilha
- **openpyxl** — suporte a arquivos `.xlsx`
- **smtplib** — envio de e-mail via SMTP (nativo do Python)
- **python-dotenv** — gerenciamento de variáveis de ambiente

---

## 📁 Estrutura do Projeto

```
monitor-vencimentos/
├── monitor.py          ← Script principal
├── gerar_exemplo.py    ← Gera planilha de teste
├── requirements.txt
├── .env.example        ← Copie para .env e configure
└── .gitignore
```

---

## ⚡ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/monitor-vencimentos.git
cd monitor-vencimentos
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```
Edite o `.env` com suas credenciais de e-mail.

> **Gmail:** gere uma *senha de app* em [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) e use no lugar da senha normal.

---

## ▶️ Como usar

### Gerar planilha de exemplo (para teste)
```bash
python gerar_exemplo.py
```

### Rodar o monitor
```bash
# Alerta padrão (3 dias, definido no .env)
python monitor.py planilha_exemplo.xlsx

# Alerta personalizado (ex: 7 dias)
python monitor.py planilha_exemplo.xlsx --dias 7

# Apenas gerar relatório CSV, sem enviar e-mail
python monitor.py planilha_exemplo.xlsx --so-relatorio
```

---

## 📋 Formato da Planilha

A planilha Excel deve conter pelo menos estas colunas:

| cliente | valor | vencimento | status |
|---------|-------|------------|--------|
| João Silva | 350.00 | 15/04/2025 | pendente |
| Maria Lima | 800.00 | 10/04/2025 | atrasado |

- **vencimento:** aceita formatos `dd/mm/aaaa` ou `aaaa-mm-dd`
- **status:** parcelas com status `pago`, `pagamento_dia` ou `cancelado` são ignoradas
- Colunas extras (telefone, observação etc.) são aceitas sem problema

---

## 📤 Saídas

- **E-mail HTML** com tabela formatada dos vencimentos encontrados
- **Arquivo CSV** (`relatorio_AAAA-MM-DD.csv`) salvo localmente
- **Log** (`monitor.log`) com registro de cada execução

---

## ⏰ Automatizar com agendador

### Windows (Agendador de Tarefas)
Crie uma tarefa que execute diariamente:
```
python C:\caminho\monitor.py C:\caminho\planilha.xlsx
```

### Linux / Mac (cron)
```bash
crontab -e

# Executa todo dia às 8h da manhã
0 8 * * * /caminho/venv/bin/python /caminho/monitor.py /caminho/planilha.xlsx
```

---

## 🔒 Segurança

- Credenciais ficam apenas no `.env` (nunca sobe pro Git)
- Use sempre *senha de app* em vez da senha real da conta
- O `.gitignore` já exclui `.env`, logs e relatórios gerados
