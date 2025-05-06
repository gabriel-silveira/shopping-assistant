import re
from typing import Optional, Dict, Any

def extract_intention(texto: str) -> str:
    """
    Remove palavras que diluem a semântica de uma consulta
    e retorna uma versão enxuta focada em intenção de produto.
    """
    texto = texto.lower()

    # Frases introdutórias e educadas comuns que não ajudam semanticamente
    expressoes_ineuteis = [
        "bom dia", "boa tarde", "boa noite",
        "oi", "olá", "tudo bem", "como vai",
        "gostaria de", "preciso de", "queria", "desejo",
        "venho por meio deste", "estou interessado em",
        "por favor", "seria possível", "poderia me informar",
        "quero", "necessito de", "tem como",
        "informações sobre", "gostaria", "me passe", "me envie"
    ]

    # Substitui expressões inúteis por vazio
    for exp in expressoes_ineuteis:
        texto = texto.replace(exp, "")

    # Remove pontuação
    texto = re.sub(r"[^\w\s]", "", texto)

    # Remove stopwords (opcional: pode usar uma lista mais completa ou nltk)
    stopwords_basicas = [
        "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
        "em", "para", "por", "com", "e", "a", "o", "que", "sobre",
        "no", "na", "nos", "nas", "me", "te", "se", "lhe"
    ]
    palavras = texto.split()
    palavras_filtradas = [p for p in palavras if p not in stopwords_basicas]

    # Retorna a intenção filtrada
    return " ".join(palavras_filtradas).strip()

def extract_customer_name(text: str) -> Optional[str]:
    """Extract customer name from text using regex patterns."""
    # Primeiro tenta padrões específicos
    name_patterns = [
        r"(?i)meu nome (?:é|e) ([^\n.,]+)",
        r"(?i)me chamo ([^\n.,]+)",
        r"(?i)^(?:eu )?sou (?:o|a) ([^\n.,]+)",
        r"(?i)pode me chamar de ([^\n.,]+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    # Se não encontrou padrões específicos, verifica se o texto é um nome válido
    text = text.strip()
    
    # Critérios para considerar um texto como nome:
    # 1. Deve ter entre 2 e 50 caracteres
    # 2. Deve conter apenas letras, espaços e alguns caracteres especiais (como hífen para nomes compostos)
    # 3. Deve ter pelo menos duas palavras (nome e sobrenome)
    # 4. Não deve conter palavras comuns que indicam que não é um nome
    
    # Palavras comuns que indicam que o texto não é um nome
    non_name_indicators = {
        'ola', 'oi', 'bom', 'boa', 'dia', 'tarde', 'noite', 'quero', 'preciso', 'gostaria',
        'sim', 'nao', 'obrigado', 'obrigada', 'ok', 'certo', 'entendi', 'empresa', 'email',
        'telefone', 'contato', 'produto', 'orcamento', 'valor', 'preco'
    }
    
    # Remove caracteres especiais exceto espaços e hífen
    clean_text = re.sub(r'[^a-zA-ZÀ-ÿ\s-]', '', text)
    words = clean_text.split()
    
    # Verifica se parece ser um nome válido
    if (len(words) >= 2 and  # Pelo menos duas palavras
        2 <= len(clean_text) <= 50 and  # Tamanho razoável
        all(len(word) >= 2 for word in words) and  # Cada palavra tem pelo menos 2 caracteres
        not any(word.lower() in non_name_indicators for word in words) and  # Não contém palavras comuns
        all(word.isalpha() or '-' in word for word in words)):  # Apenas letras e hífen
        return clean_text
    
    return None

def extract_customer_email(text: str) -> Optional[str]:
    """Extract customer email from text using regex patterns."""
    email_patterns = [
        r"(?i)meu e-?mail (?:é|e) ([^\s]+@[^\s]+)",
        r"(?i)([^\s]+@[^\s]+)"
    ]
    
    for pattern in email_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None

def extract_customer_phone(text: str) -> Optional[str]:
    """Extract customer phone from text using regex patterns."""
    phone_patterns = [
        r"(?i)meu (?:número|telefone|celular|contato) (?:é|e) ([0-9\s-]+)",
        r"(?i)([0-9]{2}[\s-]?[0-9]{4,5}[\s-]?[0-9]{4})"
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            # Remove espaços e hífens do número
            phone = re.sub(r'[\s-]', '', match.group(1))
            # Formata o número como XX XXXXX-XXXX ou XX XXXX-XXXX
            if len(phone) == 11:
                return f"{phone[:2]} {phone[2:7]}-{phone[7:]}"
            elif len(phone) == 10:
                return f"{phone[:2]} {phone[2:6]}-{phone[6:]}"
            return phone
    return None

def extract_customer_company(text: str) -> Optional[str]:
    """Extract customer company from text using regex patterns."""
    company_patterns = [
        r"(?i)(?:da |da empresa |empresa )([^\n.,]+)",
        r"(?i)trabalho (?:na|no|em) ([^\n.,]+)",
        r"(?i)(?:minha|nossa) empresa (?:é|e|se chama) ([^\n.,]+)"
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None

def extract_quote_details(text: str) -> Dict[str, Any]:
    """Extract quote details from text using regex patterns."""
    details = {}
    
    # Product name patterns
    product_patterns = [
        r"(?i)(?:quero|preciso|gostaria|necessito)(?:\s+de)?\s+([^.,]+)",
        r"(?i)produto:?\s+([^.,]+)",
        r"(?i)item:?\s+([^.,]+)",
        r"(?i)pedido:?\s+([^.,]+)"
    ]
    for pattern in product_patterns:
        if match := re.search(pattern, text):
            details['product_name'] = match.group(1).strip()
            break
    
    # Quantity patterns
    quantity_patterns = [
        r"(?i)(\d+)\s+(?:unidades?|peças?|itens?|produtos?)",
        r"(?i)quantidade:?\s*(\d+)",
        r"(?i)(?:quero|preciso|gostaria|necessito)(?:\s+de)?\s+(\d+)",
        r"(\d+)\s*(?:un|pc|pç)"
    ]
    for pattern in quantity_patterns:
        if match := re.search(pattern, text):
            details['quantity'] = int(match.group(1))
            break
    
    # Specifications patterns
    spec_patterns = [
        r"(?i)(?:com|de)\s+(\d+\s*(?:mm|cm|m|pol|polegadas?))",
        r"(?i)especificações?:?\s+([^.]+)",
        r"(?i)(?:tamanho|medida|dimensão|diâmetro):?\s+([^.,]+)",
        r"(?i)material:?\s+([^.,]+)",
        r"(?i)(?:em|no)?\s*(?:tamanho|medida|dimensão|diâmetro)\s+(?:de\s+)?(\d+\s*(?:mm|cm|m|pol|polegadas?))",
        r"(?i)(?:de\s+)?(\d+\s*(?:mm|cm|m|pol|polegadas?))\s+(?:de\s+)?(?:tamanho|medida|dimensão|diâmetro)"
    ]
    for pattern in spec_patterns:
        if match := re.search(pattern, text):
            details['specifications'] = match.group(1).strip()
            break
    
    # Additional notes patterns
    note_patterns = [
        r"(?i)obs(?:ervações?)?:?\s+([^.]+)",
        r"(?i)notas?:?\s+([^.]+)",
        r"(?i)adicionais?:?\s+([^.]+)",
        r"(?i)também\s+(?:quero|preciso|gostaria)\s+([^.]+)"
    ]
    for pattern in note_patterns:
        if match := re.search(pattern, text):
            details['additional_notes'] = match.group(1).strip()
            break
    
    return details