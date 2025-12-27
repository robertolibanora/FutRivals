# Guida Migrazione da Excel a SQLite

## Panoramica
L'applicazione è stata migrata da un sistema basato su file Excel a un database SQLite. Questo permette di modificare i dati direttamente dall'interfaccia web admin senza dover aggiornare manualmente il file Excel.

## Configurazione Iniziale

### 1. Installazione Dipendenze
Assicurati di avere installate tutte le dipendenze necessarie:
```bash
pip install -r requirements.txt
```

### 2. Configurazione Variabili d'Ambiente

L'applicazione usa variabili d'ambiente per tutte le configurazioni sensibili. 

**IMPORTANTE**: Prima di avviare l'applicazione, devi creare un file `.env` basato su `.env.example`:

```bash
cp .env.example .env
```

Poi modifica il file `.env` con le tue configurazioni:

```env
# Chiave segreta per Flask (IMPORTANTE: cambia in produzione!)
SECRET_KEY=la-tua-chiave-segreta-sicura

# Credenziali Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=tua-password-sicura

# Configurazione Server
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=1234

# Database
DB_NAME=torneo.db
```

**Genera una SECRET_KEY sicura**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

⚠️ **SICUREZZA**: 
- Il file `.env` è escluso dal repository Git (vedi `.gitignore`)
- **NON** committare mai il file `.env` con credenziali reali
- Cambia **sempre** le credenziali di default prima di mettere in produzione

## Passi per la Migrazione

### 1. Esegui lo Script di Migrazione
Esegui il seguente comando per importare tutti i dati dall'Excel al database:

```bash
python migrate_excel_to_db.py
```

Questo script:
- Crea il database `torneo.db` se non esiste
- Importa tutte le squadre dal foglio "Classifiche"
- Importa tutti i giocatori dal foglio "Rose"
- Importa tutte le partite dal foglio "Calendario Partite"
- Importa il vincitore finale dal foglio "Finale"
- Calcola automaticamente la classifica dalle partite giocate

### 2. Verifica il Database
Dopo la migrazione, verifica che il file `torneo.db` sia stato creato nella directory principale del progetto.

### 3. Accesso all'Area Admin

#### Credenziali
Le credenziali admin sono configurate nel file `.env`:
- **Username**: Valore di `ADMIN_USERNAME` (default: `admin`)
- **Password**: Valore di `ADMIN_PASSWORD` (default: `admin123`)

⚠️ **IMPORTANTE**: Cambia queste credenziali nel file `.env` prima di mettere in produzione!

#### Accesso
1. Vai su `/admin` nel tuo browser
2. Inserisci le credenziali
3. Sei ora nella dashboard admin

### 4. Funzionalità Admin

#### Gestione Partite
- **Aggiungere Partite**: Compila il form nella sezione "Aggiungi Nuova Partita"
- **Modificare Risultati**: Inserisci i risultati nella tabella partite e clicca "Salva"
- **Eliminare Partite**: Clicca il pulsante "Elimina" accanto alla partita desiderata

#### Gestione Marcatori
- **Aggiornare Goal**: Modifica il numero di goal nella tabella giocatori e clicca "Aggiorna"

#### Aggiornamento Automatico Classifica
La classifica viene calcolata automaticamente quando:
- Modifichi un risultato di una partita
- Elimini una partita
- Lo script di migrazione viene eseguito

## Struttura Database

### Tabelle
1. **squadre**: Informazioni sulle squadre (nome, logo, girone, statistiche)
2. **giocatori**: Giocatori con i loro goal totali
3. **partite**: Tutte le partite del calendario con risultati
4. **marcatori**: Tracciamento dettagliato dei marcatori (per uso futuro)
5. **vincitore_finale**: Squadra vincitrice del torneo

## Note Importanti

- Il file Excel originale (`DATITORNEO.xlsx`) non viene più utilizzato dall'applicazione dopo la migrazione
- Puoi mantenere il file Excel come backup, ma tutte le modifiche vanno fatte tramite l'interfaccia admin
- Il database SQLite (`torneo.db`) deve essere incluso nel backup del progetto
- La classifica viene ricalcolata automaticamente basandosi sui risultati delle partite

## Risoluzione Problemi

### Il database non si aggiorna
Assicurati che il file `torneo.db` non sia bloccato e che l'applicazione abbia i permessi di scrittura.

### La classifica non è corretta
Esegui manualmente l'aggiornamento della classifica chiamando la funzione `update_classifica_from_partite()` da un terminale Python:
```python
from database import update_classifica_from_partite
update_classifica_from_partite()
```

### Perdita dati
In caso di problemi, puoi sempre rieseguire lo script di migrazione (dopo aver fatto un backup del database esistente).

