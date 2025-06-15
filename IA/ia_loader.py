from transformers import AutoTokenizer, AutoModelForCausalLM
import os

def load_local_model():
    # Corrige proprement le chemin absolu
    model_path = os.path.abspath("IA/modele_local")

    print(f"Chargement du modèle depuis : {model_path}")

    # Chargement du tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        local_files_only=True
    )

    # Chargement du modèle
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True
    )

    return tokenizer, model
