from transformers import pipeline

pipe = pipeline("text-classification", model="./intent_model_final")

def get_intent(text):
    result = pipe(text, return_all_scores=True)
    return result[0]

print(get_intent("De ce nu functioneaza aplicatia asta"))
