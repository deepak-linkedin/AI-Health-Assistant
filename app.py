import random
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from deep_translator import GoogleTranslator
import streamlit as st

# load data
df = pd.read_csv(r'dataset - Sheet1.csv')
# print(df.head());
@st.cache_resource
def load_model_and_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    disease_embeddings = model.encode(
        df['disease'].tolist(),
        convert_to_tensor=True
    )
    return model, disease_embeddings

# Call the cached function
model, disease_embeddings = load_model_and_embeddings()

# Streamlit UI
st.title("Medical Chatbot 🤖")
user_input = st.text_input("Ask a question:")

#language selection
language_choice = st.selectbox("Select Language",[
    "English","Telugu","Hindi","Tamil","Kannada","Malayalam","Gujarati","Korean",
    "Turkish","German","French","Arabic","Urdu","Tamil","Japanese"
])

#Languag-e codes
language_codes = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Gujarati": "gu",
    "Korean": "ko",
    "Turkish": "tr",
    "German": "de",
    "French": "fr",
    "Arabic": "ar",
    "Urdu": "ur",
    "Tamil": "ta",
    "Japanese": "ja",
}
# medical keywords, if user input has less similarity with those in dataset,thse will help
medical_keywords = {
    "fever" : "It sounds like you may have a fever. Stay hydrated and consider seeing a doctor if symptoms persist.",
    "cough" : "A persistent cough might be due to an infection or allergy. Try warm fluids and rest.",
    "headache" : "Headaches can have many causes, including stress and dehydration. Consider resting and drinking water.",
    "cold" : "Common colds usually go away on their own. Stay warm, drink fluids, and get rest."
}
# Health tips categorized by keywords
health_tips = {
    "sleep" :[
        "Try to get at least 7-8 hours of sleep each night.",
        "Establish a regular sleep routine to improve sleep quality.",
        "Avoid screens before bed to help your mind relax.",
    ],
    "energy":[
        "Make sure you're eating a balanced diet to maintain energy.",
        "Exercise regularly to boost your energy levels.",
        "Stay hydrated throughout the day to avoid fatigue.",
    ],
    "stress":[
        "Take short breaks throughout the day to reduce stress.",
        "Practice mindfulness or meditation to help manage stress.",
        "Engage in physical activity to reduce anxiety and stress.",
    ],
    "general":[
        "Drink plenty of water throughout the day.",
        "Get at least 30 minutes of exercise every day.",
        "Eat a balanced diet rich in fruits and vegetables.",
    ],
}

# def translate_text(text,dest_language='en'):
#     return GoogleTranslator(source='auto',target=dest_language).translate(text)

@st.cache_data(ttl=3600)
def translate_text(text,dest_language):
    if not text:
        return text
    try :
        return GoogleTranslator(source="auto",target=dest_language).translate()
    except Exception as e:
        print(f"Translation error: {e}")
        return text
                                

def get_personalized_health_tip(user_input):
    user_input_lower = user_input.lower()

    if "tired" in user_input or "fatigue" in user_input_lower :
        return random.choice(health_tips["energy"])
    elif "sleep" in user_input_lower or "rest" in user_input_lower :
        return random.choice(health_tips["sleep"])
    elif "stress" in user_input_lower or "anxious" in user_input_lower :
        return random.choice(health_tips['stress'])
    else:
        return random.choice(health_tips["general"])

def find_best_cure(user_input):
    user_input_embedding = model.encode(user_input,convert_to_tensor=True)
    #disease_embeddings = model.encode(df['disease'].tolist(),convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(user_input_embedding,disease_embeddings)[0]
    best_match_idx = similarities.argmax().item()
    best_match_score = similarities[best_match_idx].item()

    #Similarity threshold for valid matches
    SIMILARITY_THRESHOLD = 0.5

    if best_match_score < SIMILARITY_THRESHOLD :
        # check for keywords in user input
        for keyword,response in medical_keywords.items() :
            if keyword in user_input.lower() :
                return response
        # if no keywords match, cannot say correct response
        return "I'm sorry, I don't have enough information on this. Please consult a healthcare professional."
    
    return df.iloc[best_match_idx]['cure']


# button for response
if st.button("Get Response"):
    if user_input :
        response = find_best_cure(user_input)
        # Translate response to selected language
        translated_response = translate_text(response,dest_language=language_codes[language_choice])
        st.write(f"**My Suggestion is:** {translated_response}")
        st.write("*Please note, the translation is provided by AI and might not be perfect.*")

# button to get a personalized health tip
if st.button("Get a Personalized Tip"):
    if user_input:
        personalized_tip = get_personalized_health_tip(user_input)
        translated_tip = translate_text(personalized_tip,dest_language=language_codes[language_choice])
        st.write(f"**Health Tip:** {translated_tip}")
        st.write("*Please note, the translation is provided by AI and might not be perfect.*")
