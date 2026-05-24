# proiect

## Sarcina 3 - Backend, API si Interfata

Aplicatie demo pentru chatbot de suport social media. Partea aceasta leaga componentele colegilor intr-un produs utilizabil:

- Backend FastAPI cu endpoint `/chat`
- Interfata Streamlit pentru demo live
- Orchestrare intre intent classification si generatorul LLM
- Mock pentru Sarcina 1, pana cand modelul final este gata
- Raspunsuri generate prin Groq LLM, fara fallback local pentru raspunsul chatbotului

## Structura

```text
app/
  main.py                         # FastAPI endpoints
  schemas.py                      # Contractul JSON comun
  config.py                       # Setari din variabile de mediu
  services/
    intent_service.py             # Mock Sarcina 1
    dialogue_service.py           # Adapter Sarcina 2 / Groq LLM
    chat_orchestrator.py          # Leaga intentul de raspuns
streamlit_app.py                  # Interfata vizuala pentru demo
requirements.txt
.env.example
```

## Contract API

Input pentru `/chat`:

```json
{
  "user_id": "user_001",
  "message": "Nu imi merge aplicatia"
}
```

Output:

```json
{
  "user_id": "user_001",
  "message": "Nu imi merge aplicatia",
  "response": "Imi pare rau pentru problema intampinata...",
  "intent": "complaint",
  "confidence": 0.88,
  "entities": {"issue": "eroare aplicatie"},
  "was_filtered": false,
  "llm_provider": "groq"
}
```

Cand Sarcina 1 este gata, se inlocuieste functia `detect_intent_mock()` din `app/services/intent_service.py`. Atat timp cat returneaza `intent`, `confidence` si `entities`, backend-ul si Streamlit nu trebuie schimbate.

## Rulare Locala

1. Creeaza mediul si instaleaza dependintele:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configureaza cheia Groq:

```bash
cp .env.example .env
export GROQ_API_KEY="cheia_ta_groq"
```

Aplicatia nu genereaza raspunsuri mock pentru chatbot. Daca cheia Groq lipseste sau este invalida, endpoint-ul `/chat` returneaza eroarea reala.

3. Porneste backend-ul:

```bash
uvicorn app.main:app --reload --port 8000
```

Documentatia interactiva este disponibila la:

```text
http://localhost:8000/docs
```

4. Porneste interfata Streamlit intr-un terminal separat:

```bash
streamlit run streamlit_app.py
```

Streamlit se va deschide de obicei la:

```text
http://localhost:8501
```

## Endpoint-uri

- `GET /health` - verifica statusul backend-ului si modul LLM
- `POST /chat` - primeste mesajul utilizatorului si returneaza raspunsul chatbotului
- `POST /reset/{user_id}` - reseteaza conversatia pentru un utilizator
- `GET /history/{user_id}` - afiseaza istoricul curent
- `GET /logs` - afiseaza interactiunile logate in memorie

## Exemplu Test Rapid

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_001","message":"Buna, am o problema cu contul meu"}'
```

## Ce Se Prezinta La Demo

1. Utilizatorul scrie un mesaj in Streamlit.
2. Streamlit trimite JSON catre `/chat`.
3. Backend-ul detecteaza intentul prin mock-ul Sarcinii 1.
4. Backend-ul trimite mesajul si intentul catre Groq LLM.
5. Raspunsul, intentul si scorul de incredere apar in interfata.
