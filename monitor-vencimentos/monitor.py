"""
Monitor de Vencimentos
Lê uma planilha Excel com parcelas e envia alertas por e-mail
para cobranças que vencem nos próximos dias.
"""

import smtplib
import logging
import os
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ── Configurações ──────────────────────────────────────────────────────────────

DIAS_ALERTA = int(os.getenv("DIAS_ALERTA", 3))          # quantos dias antes de vencer
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

COLUNAS_ESPERADAS = {"cliente", "valor", "vencimento", "status"}

# ── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("monitor.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── Funções ────────────────────────────────────────────────────────────────────

def carregar_planilha(caminho: str) -> pd.DataFrame:
    """Carrega e valida a planilha Excel."""
    log.info(f"Carregando planilha: {caminho}")
    try:
        df = pd.read_excel(caminho)
    except FileNotFoundError:
        raise SystemExit(f"[ERRO] Arquivo não encontrado: {caminho}")

    df.columns = df.columns.str.strip().str.lower()

    faltando = COLUNAS_ESPERADAS - set(df.columns)
    if faltando:
        raise SystemExit(f"[ERRO] Colunas faltando na planilha: {faltando}")

    df["vencimento"] = pd.to_datetime(df["vencimento"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["vencimento"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    log.info(f"{len(df)} registros carregados.")
    return df


def filtrar_vencimentos(df: pd.DataFrame, dias: int) -> pd.DataFrame:
    """Filtra parcelas pendentes que vencem dentro do prazo configurado."""
    hoje = date.today()
    limite = hoje + timedelta(days=dias)

    mask = (
        (df["vencimento"].dt.date >= hoje) &
        (df["vencimento"].dt.date <= limite) &
        (~df["status"].str.strip().str.lower().isin(["pago", "pagamento_dia", "cancelado"]))
    )

    resultado = df[mask].copy()
    log.info(f"{len(resultado)} parcela(s) vencem nos próximos {dias} dia(s).")
    return resultado


def formatar_email(parcelas: pd.DataFrame, dias: int) -> tuple[str, str]:
    """Gera o assunto e corpo do e-mail."""
    hoje = date.today().strftime("%d/%m/%Y")
    assunto = f"⚠️ {len(parcelas)} vencimento(s) nos próximos {dias} dias – {hoje}"

    linhas_html = ""
    for _, row in parcelas.iterrows():
        venc = row["vencimento"].strftime("%d/%m/%Y")
        valor = f"R$ {row['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        status = str(row["status"]).strip()
        linhas_html += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ddd">{row['cliente']}</td>
            <td style="padding:8px;border:1px solid #ddd;text-align:center">{venc}</td>
            <td style="padding:8px;border:1px solid #ddd;text-align:right">{valor}</td>
            <td style="padding:8px;border:1px solid #ddd;text-align:center">{status}</td>
        </tr>"""

    corpo = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333">
        <h2 style="color:#c0392b">⚠️ Alerta de Vencimentos</h2>
        <p>As seguintes parcelas vencem nos próximos <strong>{dias} dias</strong>:</p>
        <table style="border-collapse:collapse;width:100%;max-width:700px">
            <thead>
                <tr style="background:#2c3e50;color:#fff">
                    <th style="padding:10px;border:1px solid #ddd">Cliente</th>
                    <th style="padding:10px;border:1px solid #ddd">Vencimento</th>
                    <th style="padding:10px;border:1px solid #ddd">Valor</th>
                    <th style="padding:10px;border:1px solid #ddd">Status</th>
                </tr>
            </thead>
            <tbody>{linhas_html}</tbody>
        </table>
        <p style="margin-top:20px;font-size:12px;color:#888">
            Enviado automaticamente em {date.today().strftime("%d/%m/%Y")} — Monitor de Vencimentos
        </p>
    </body></html>
    """
    return assunto, corpo


def enviar_email(assunto: str, corpo_html: str) -> None:
    """Envia o e-mail via SMTP."""
    if not all([EMAIL_REMETENTE, EMAIL_SENHA, EMAIL_DESTINATARIO]):
        log.warning("Credenciais de e-mail não configuradas. Pulando envio.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor:
            servidor.ehlo()
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
        log.info(f"E-mail enviado para {EMAIL_DESTINATARIO}.")
    except smtplib.SMTPException as exc:
        log.error(f"Falha ao enviar e-mail: {exc}")


def exportar_relatorio(parcelas: pd.DataFrame) -> None:
    """Salva um relatório CSV com os vencimentos encontrados."""
    if parcelas.empty:
        return
    caminho = f"relatorio_{date.today().isoformat()}.csv"
    parcelas.to_csv(caminho, index=False, sep=";", encoding="utf-8-sig")
    log.info(f"Relatório salvo em: {caminho}")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Monitor de Vencimentos")
    parser.add_argument("planilha", help="Caminho para o arquivo Excel (.xlsx)")
    parser.add_argument("--dias", type=int, default=DIAS_ALERTA,
                        help="Dias de antecedência para alertar (padrão: 3)")
    parser.add_argument("--so-relatorio", action="store_true",
                        help="Gera apenas o relatório CSV, sem enviar e-mail")
    args = parser.parse_args()

    df = carregar_planilha(args.planilha)
    vencimentos = filtrar_vencimentos(df, args.dias)

    if vencimentos.empty:
        log.info("Nenhum vencimento encontrado no período. Nada a fazer.")
        return

    exportar_relatorio(vencimentos)

    if not args.so_relatorio:
        assunto, corpo = formatar_email(vencimentos, args.dias)
        enviar_email(assunto, corpo)
    else:
        log.info("Modo --so-relatorio ativo. E-mail não enviado.")


if __name__ == "__main__":
    main()
