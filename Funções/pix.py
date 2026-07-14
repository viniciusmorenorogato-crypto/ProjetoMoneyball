"""Geração de Pix "copia e cola" (BR Code) e QR code para o botão de apoio.

Implementa o payload EMV-QRCPS estático definido no Manual de Padrões para
Iniciação do Pix (Banco Central do Brasil), sem valor fixo — quem doa escolhe
o valor no app do banco.
"""
import unicodedata


def _sem_acentos(texto):
    """Remove acentos e caracteres fora do padrão aceito pelo BR Code."""
    normalizado = unicodedata.normalize('NFKD', str(texto))
    return ''.join(c for c in normalizado if c.isascii() and c.isprintable())


def _campo(id_campo, valor):
    """Monta um campo TLV do EMV: ID (2 dígitos) + tamanho (2 dígitos) + valor."""
    valor = str(valor)
    return f"{id_campo}{len(valor):02d}{valor}"


def _crc16_ccitt(dados):
    """CRC-16/CCITT-FALSE (polinômio 0x1021, inicial 0xFFFF), exigido pelo BR Code."""
    crc = 0xFFFF
    for byte in dados.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def gerar_payload_pix(chave, nome, cidade, txid="***"):
    """Gera a string "Pix copia e cola" para uma chave Pix estática sem valor fixo.

    chave: qualquer tipo de chave Pix (e-mail, telefone +55..., CPF/CNPJ ou aleatória)
    nome: nome do recebedor (máx. 25 caracteres, sem acentos)
    cidade: cidade do recebedor (máx. 15 caracteres, sem acentos)
    """
    chave = str(chave).strip()
    nome = _sem_acentos(nome)[:25].strip() or "RECEBEDOR"
    cidade = _sem_acentos(cidade)[:15].strip().upper() or "BRASIL"

    conta = _campo("00", "br.gov.bcb.pix") + _campo("01", chave)
    payload = (
        _campo("00", "01")            # Payload Format Indicator
        + _campo("26", conta)         # Merchant Account Information (Pix)
        + _campo("52", "0000")        # Merchant Category Code
        + _campo("53", "986")         # Moeda: BRL
        + _campo("58", "BR")          # País
        + _campo("59", nome)          # Nome do recebedor
        + _campo("60", cidade)        # Cidade do recebedor
        + _campo("62", _campo("05", txid))  # Dados adicionais (txid)
        + "6304"                      # ID + tamanho do CRC, incluídos no cálculo
    )
    return payload + _crc16_ccitt(payload)


def gerar_qr_pix(payload):
    """Gera a imagem PIL do QR code do payload. Retorna None se a lib não estiver instalada."""
    try:
        import qrcode
    except ImportError:
        return None
    qr = qrcode.QRCode(border=2, box_size=8)
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").get_image()
