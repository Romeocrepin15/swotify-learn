from transformers import AutoTokenizer, AutoModelForCausalLM

# Choisis ton modèle ici (public et gratuit)
model_id = "gpt2"  # ou "mistralai/Mistral-7B-Instruct" si tu as accès

# Téléchargement + sauvegarde locale dans ./IA/modele_local/
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Sauvegarde locale du modèle
model.save_pretrained("./IA/modele_local/")
tokenizer.save_pretrained("./IA/modele_local/")

print("✅ Modèle et tokenizer téléchargés localement avec succès.")
