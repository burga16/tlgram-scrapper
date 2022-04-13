from deep_translator import GoogleTranslator

def translateMsg(msg):
    traductor = GoogleTranslator(source='auto', target='en')
    resultado = traductor.translate(msg)
    return resultado