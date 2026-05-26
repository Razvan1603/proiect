# proiect
##Model de Clasificare a Intențiilor

Acest repository găzduiește un model de procesare a limbajului natural bazat pe arhitectura Romanian BERT, antrenat pentru clasificarea textelor în 7 categorii distincte.

Structura modelului:
Fișierele esențiale pentru rularea modelului se află în folderul intent_model_final/:
config.json – Conține arhitectura modelului și maparea ID-urilor către clase.
tokenizer.json & tokenizer_config.json – Fișiere necesare pentru pre-procesarea textului.

DESCARCA_MODELUL_DE_AICI.txt – Link către stocarea externă (Google Drive) pentru fișierul de greutăți model.safetensors (~400MB).

## Antrenare și Validare
Modelul a fost antrenat pe un set de date specific, respectând următoarele rigori tehnice:

Split de Date: S-a utilizat o metodă de împărțire 80% antrenare / 20% testare.
Randomizare: Datele au fost amestecate aleatoriu și stratificate pentru a menține proporția claselor în ambele seturi.
Performanță: Modelul a fost evaluat pe setul de test (date nevăzute), obținând rezultate optime pentru integrarea în producție.

##Categorii Clasificate (Intenții)
Cele 7 clase pe care modelul le poate identifica sunt:
- [SALUT]
- [INTREBARE]
- [HELP]
- [RECLAMATIE]
- [MULTUMIRE]
- [PREZENTARE]
- [SMALL_TALK]


## Backend, API si Interfata

Aplicatie demo pentru chatbot de suport social media.

- Backend FastAPI cu endpoint `/chat`
- Interfata Streamlit pentru demo live
- Orchestrare intre intent classification real si generatorul LLM
- Model Sarcina 1 incarcat din `model_final/model.safetensors`
- Raspunsuri generate prin Groq LLM, fara fallback local pentru raspunsul chatbotului

## Structura

```text
app/
  main.py                         # FastAPI endpoints
  schemas.py                      # Contractul JSON comun
  config.py                       # Setari din variabile de mediu
  services/
    intent_classifier.py          # Incarca model_final/model.safetensors
    intent_service.py             # Adapter Sarcina 1
    dialogue_service.py           # Adapter Sarcina 2 / Groq LLM
    chat_orchestrator.py          # Leaga intentul de raspuns
streamlit_app.py                  # Interfata vizuala pentru demo
model_final/model.safetensors     # Greutati BERT locale, tinute in Drive/Git LFS, nu in Git
start.sh                          # Pornire backend + Streamlit
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

Intentul nu mai este mock. Backend-ul foloseste obligatoriu modelul BERT din `model_final/model.safetensors`, prin `transformers.pipeline`. Daca fisierul `model.safetensors` sau dependintele `transformers`, `torch`, `safetensors` lipsesc, endpoint-ul returneaza eroare in loc sa foloseasca alt classifier. Adapterul public pentru este `detect_intent()` din `app/services/intent_service.py`, iar acesta returneaza mereu formatul comun: `intent`, `confidence`, `entities`.

Notebook-ul `notebooks/Antrenarea_modelului.ipynb` descrie varianta Transformer/BERT. Greutatile mari ale modelului nu trebuie urcate direct in GitHub; sunt pastrate prin Drive/Git LFS, iar `.gitignore` exclude `model_final/model.safetensors`.

## Rulare Locala

### Instalare de la zero

1. Descarca proiectul:

```bash
git clone git@github.com:Razvan1603/proiect.git
cd proiect
```

Daca nu ai SSH configurat pe GitHub, foloseste varianta HTTPS:

```bash
git clone https://github.com/Razvan1603/proiect.git
cd proiect
```

2. Creeaza mediul virtual si instaleaza dependintele:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Pune modelul BERT in folderul corect.

Fisierul mare `model.safetensors` nu este urcat direct in GitHub. Se descarca din link-ul din:

```text
model_final/GET_MODEL.TXT
```

Dupa descarcare, fisierul trebuie sa fie exact aici:

```text
model_final/model.safetensors
```

4. Configureaza cheia Groq.

Copiaza exemplul de configurare:

```bash
cp .env.example .env
```

Deschide `.env` si pune cheia ta:

```text
GROQ_API_KEY=cheia_ta_groq
GROQ_MODEL=llama-3.3-70b-versatile
API_BASE_URL=http://127.0.0.1:8004
USE_MOCK_LLM=false
```

Aplicatia nu genereaza raspunsuri mock pentru chatbot. Daca cheia Groq lipseste sau este invalida, endpoint-ul `/chat` returneaza eroarea reala.

5. Porneste backend-ul si interfata:

```bash
chmod +x start.sh
./start.sh
```

Streamlit se va deschide la:

```text
http://localhost:8504
```

6. Verifica rapid ca modelul BERT este folosit:

```bash
curl -X POST http://127.0.0.1:8004/intent \
  -H "Content-Type: application/json" \
  -d '{"message":"Buna, am eroarea 403 cand incerc sa ma loghez"}'
```

In raspuns trebuie sa apara:

```json
"model_backend": "bert_safetensors"
```

### Pornire Manuala

Daca nu vrei sa folosesti `start.sh`, porneste backend-ul manual:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8004 --reload
```

Documentatia interactiva este disponibila la:

```text
http://localhost:8004/docs
```

Si interfata Streamlit intr-un terminal separat:

```bash
API_BASE_URL=http://127.0.0.1:8004 streamlit run streamlit_app.py --server.port 8504
```

Streamlit se va deschide de obicei la:

```text
http://localhost:8504
```

## Endpoint-uri

- `GET /health` - verifica statusul backend-ului si modul LLM
- `POST /intent` - returneaza intentul detectat de Sarcina 1
- `POST /chat` - primeste mesajul utilizatorului si returneaza raspunsul chatbotului
- `POST /reset/{user_id}` - reseteaza conversatia pentru un utilizator
- `GET /history/{user_id}` - afiseaza istoricul curent
- `GET /logs` - afiseaza interactiunile logate in memorie

## Exemplu Test Rapid

```bash
curl -X POST http://localhost:8004/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_001","message":"Buna, am o problema cu contul meu"}'
```

Test intent separat:

```bash
curl -X POST http://localhost:8004/intent \
  -H "Content-Type: application/json" \
  -d '{"message":"Buna, am eroarea 403 cand incerc sa ma loghez"}'
```

## Funcționalitatea proiectului

1. Utilizatorul scrie un mesaj in Streamlit.
2. Streamlit trimite JSON catre `/chat`.
3. Backend-ul detecteaza intentul cu modelul antrenat.
4. Backend-ul trimite mesajul si intentul catre Groq LLM.
5. Raspunsul apare in interfata. Detaliile tehnice se pot afisa/ascunde din butonul `Arata analiza intentului`, unde apar intentul ales, confidence, providerul LLM si probabilitatile pentru toate intenturile evaluate de BERT.
