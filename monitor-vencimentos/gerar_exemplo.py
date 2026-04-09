"""
Gera uma planilha Excel de exemplo para testar o monitor.
Execute: python gerar_exemplo.py
"""

from datetime import date, timedelta
import random
import pandas as pd

hoje = date.today()

clientes = [
    "João da Silva",
    "Maria Oliveira",
    "Carlos Souza",
    "Ana Paula Lima",
    "Pedro Costa",
    "Fernanda Rocha",
    "Lucas Martins",
    "Juliana Ferreira",
]

status_opcoes = ["pendente", "pendente", "pendente", "atrasado", "pago", "inadimplente"]

registros = []
for i, cliente in enumerate(clientes):
    vencimento = hoje + timedelta(days=random.randint(-5, 10))
    registros.append({
        "cliente": cliente,
        "valor": round(random.uniform(150, 2000), 2),
        "vencimento": vencimento.strftime("%d/%m/%Y"),
        "status": random.choice(status_opcoes),
        "telefone": f"(31) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "observacao": "Gerado automaticamente",
    })

df = pd.DataFrame(registros)
df.to_excel("planilha_exemplo.xlsx", index=False)
print(f"✅ planilha_exemplo.xlsx criada com {len(df)} registros.")
print(f"   Rode: python monitor.py planilha_exemplo.xlsx")
