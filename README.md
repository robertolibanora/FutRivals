# Fut Rivals - Torneo Estivo

## Avvio rapido

1. Assicurati di avere Python 3.10+ e pip installato.
2. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```
3. Avvia l'app:
   ```
   python app.py
   ```

## Struttura file Excel (dati_torneo.xlsx)

Il file viene creato automaticamente se non esiste, con 10 squadre di esempio. Puoi modificarlo con Excel o LibreOffice.

- **Foglio "Prossime Partite"**: elenca le prossime partite. Colonne: Data, Ora, Stadio, Squadra Casa, Logo Casa, Squadra Trasferta, Logo Trasferta
- **Foglio "Rose"**: elenco giocatori per squadra. Colonne: Squadra, Giocatore, Ruolo, Numero
- **Foglio "Classifiche"**: classifica per gironi. Colonne: Pos, Squadra, Girone, PG, V, N, P, GF, GS, PT, Logo
- **Foglio "Calendario Partite"**: tutte le partite del torneo. Colonne: Data, Ora, Stadio, Squadra Casa, Logo Casa, Squadra Trasferta, Logo Trasferta, Risultato

## Gestione loghi squadre

- I loghi delle squadre vanno inseriti nella cartella `static/squadre/`.
- Il nome del file del logo deve corrispondere esattamente a quello indicato nella colonna `Logo` del foglio "Classifiche" (es: `realmatadors.png`).
- Usa solo lettere, numeri, trattini o underscore nei nomi file. Evita spazi e caratteri speciali.
- Formato consigliato: PNG, quadrato o rotondo, sfondo trasparente, 200x200px o 400x400px.
- Se manca un logo, il sito mostrerà un'icona di errore o fallback.

## Personalizzazione squadre

Per cambiare nomi, loghi o gironi:
- Modifica il foglio "Classifiche" e aggiorna la colonna `Logo`.
- Carica i nuovi file PNG nella cartella `static/squadre/`.
- Puoi aggiungere o togliere squadre, ma assicurati che ogni squadra abbia un logo unico e che i nomi coincidano.

## Consigli
- Dopo ogni modifica al file Excel, ricarica la pagina per vedere i cambiamenti.
- Se aggiungi nuove squadre, aggiorna anche le rose e il calendario.
- Per tornei più grandi, puoi aggiungere altri gironi o modificare la logica di generazione delle partite.

## Come inserire loghi e sponsor

- Inserisci i loghi delle squadre in `static/squadre/` (es: `teamA.png`)
- Inserisci i loghi degli sponsor in `static/sponsors/` (es: `sponsor1.png`)

### ATTENZIONE: Come esportare i PNG

Se un logo o sponsor non si vede nel sito (compare un punto interrogativo):

1. Apri il file PNG con un editor immagini (Anteprima su Mac, Paint su Windows, GIMP, Photoshop, ecc.)
2. Fai "Esporta come…" o "Salva con nome…"
3. Scegli formato PNG, qualità massima, disattiva trasparenza se non serve
4. Sostituisci il file nella cartella del progetto
5. Ricarica la pagina (anche svuotando la cache)

Questo evita problemi di compatibilità con PNG "strani" o scaricati da WhatsApp/social. 