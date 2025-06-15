from ia_loader import load_local_model
import torch
from django.db.models import Avg
from swotify.models import Eleve, Note


# Charger modèle et tokenizer une seule fois, au lancement
tokenizer, model = load_local_model()

def get_moyenne_eleve(eleve_id):
    notes = Note.objects.filter(eleve_id=eleve_id)
    moyenne = notes.aggregate(Avg('valeur'))['valeur__avg']
    return moyenne if moyenne is not None else 0.0

def generer_reponse(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(
        inputs,
        max_new_tokens=150,
        do_sample=True,
        temperature=0.7,
        top_p=0.85,
        repetition_penalty=1.3,
        pad_token_id=tokenizer.eos_token_id
    )
    reponse = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return reponse

def repondre(question):
    prompt = f"""
    You are an assistant for SWOTify Learn. Here is the question you need to answer clearly and concisely:    {question}
    """
    reponse = generer_reponse(prompt)
    if question in reponse:
        reponse = reponse.split(question)[-1].strip()
    return reponse

def repondre_avec_bd(question, eleve_id):
    moyenne = get_moyenne_eleve(eleve_id)
    context = f"The student with ID {eleve_id} has a general average of {moyenne:.2f}."
    prompt = f"""
    You are an assistant for SWOTify Learn. Here is some important data:
    {context}
    
    Question : {question}
    """
    reponse = generer_reponse(prompt)
    if question in reponse:
        reponse = reponse.split(question)[-1].strip()
    return reponse
