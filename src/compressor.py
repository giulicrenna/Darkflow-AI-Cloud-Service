import zlib

def compress(text: str) -> str:
    text_bytes = text.encode('utf-8')
    texto_comprimido = zlib.compress(text_bytes)
    
    return texto_comprimido

def decompress(compress_text : str) -> str:
    text_bytes = zlib.decompress(compress_text)
    texto = text_bytes.decode('utf-8')
    
    return texto