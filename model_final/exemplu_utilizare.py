from transformers import pipeline

# Incarca modelul si tokenizer-ul din folderul tau
pipe = pipeline("text-classification", model="./intent_model_final")

def get_intent(text):
    # Aceasta functie scoate JSON-ul de care au ei nevoie
    result = pipe(text, return_all_scores=True)
    return result[0]

# Exemplu de utilizare
print(get_intent("De ce nu functioneaza aplicatia asta"))
