import re

def normalize_company_name(text: str) -> str:
    """
    Normalize company names for deterministic matching.
    Steps:
    - Uppercase
    - Remove punctuation
    - Collapse whitespace
    - Remove corporate suffixes
    - Optionally remove common pharma tokens (conservative)
    """
    if not text:
        return ''
    # Uppercase
    text = text.upper()
    # Remove punctuation
    text = re.sub(r'[\.,;:/\\\-\'"&()\[\]{}]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove corporate suffixes
    corp_tokens = [
        ' INC', ' INCORPORATED', ' LLC', ' LTD', ' LIMITED', ' CORP', ' CORPORATION',
        ' CO', ' COMPANY', ' PLC', ' LP', ' SA', ' BV', ' NV', ' GMBH', ' AG', ' SPA',
        ' SARL', ' AB', ' OYJ', ' KK', ' PTY'
    ]
    for token in corp_tokens:
        if text.endswith(token):
            text = text[: -len(token)]
    # Optionally remove common pharma tokens (conservative, e.g. PHARMA, PHARMACEUTICALS)
    # Uncomment if needed:
    # pharma_tokens = [' PHARMA', ' PHARMACEUTICALS', ' PHARMACEUTICAL', ' BIOSCIENCES', ' BIOPHARMA']
    # for token in pharma_tokens:
    #     if text.endswith(token):
    #         text = text[: -len(token)]
    text = text.strip()
    return text
