"""
Funzioni helper e utilities
"""
from datetime import datetime, date


def formatta_data_italiana(data_input):
    """
    Formatta una data in stile italiano: 'Lunedì-01-Gennaio-2024'
    
    Args:
        data_input: Può essere una stringa, datetime o date object
        
    Returns:
        Stringa formattata in italiano
    """
    import locale
    
    mesi_en_it = {
        "January": "Gennaio", "February": "Febbraio", "March": "Marzo",
        "April": "Aprile", "May": "Maggio", "June": "Giugno",
        "July": "Luglio", "August": "Agosto", "September": "Settembre",
        "October": "Ottobre", "November": "Novembre", "December": "Dicembre"
    }
    giorni_en_it = {
        "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì",
        "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
    }
    
    # Se è già formattata in italiano, restituiscila così com'è
    if isinstance(data_input, str) and '-' in data_input and any(day in data_input for day in giorni_en_it.values()):
        return data_input
    
    try:
        # Gestisce date, datetime e stringhe
        data = None
        if isinstance(data_input, str):
            # Prova diversi formati di data
            try:
                # Formato SQLite: 'YYYY-MM-DD'
                data = datetime.strptime(data_input, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # Altri formati comuni
                    data = datetime.strptime(data_input, '%Y/%m/%d').date()
                except ValueError:
                    # Se non riesce a parsare, restituisci la stringa originale
                    return str(data_input)
        elif isinstance(data_input, datetime):
            data = data_input.date()
        elif isinstance(data_input, date):
            data = data_input
        else:
            return str(data_input)
        
        # Usa locale C per assicurarsi che strftime restituisca nomi in inglese
        old_locale = locale.getlocale(locale.LC_TIME)
        try:
            locale.setlocale(locale.LC_TIME, 'C')
            giorno_en = data.strftime("%A")
            mese_en = data.strftime("%B")
        finally:
            # Ripristina il locale originale
            if old_locale[0]:
                try:
                    locale.setlocale(locale.LC_TIME, old_locale)
                except:
                    pass
        
        nome_giorno = giorni_en_it.get(giorno_en, giorno_en)
        nome_mese = mesi_en_it.get(mese_en, mese_en)
        # Formato: Giovedì-10-Luglio-2025
        return f"{nome_giorno}-{data.day:02d}-{nome_mese}-{data.year}"
    except Exception as e:
        print(f"Errore nella formattazione della data: {e} (input: {data_input}, type: {type(data_input)})")
        return str(data_input)

