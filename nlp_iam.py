import spacy

class NLP_IAM:
    nlp = spacy.load("en_core_web_sm")

    def extract_info(nlp,prompt):
        doc = nlp(prompt)

        action = ""
        username = ""
        permissions = []

        for token in doc:
            if token.text.lower() == "create":
                action = "create"
            if token.text.lower() == "delete":
                action = "delete"
            if token.text.lower() == "update":
                action = "update"
            if token.text.lower() == "user" or token.text.lower() == "username":
                username = token.nbor().text
            elif token.text.lower() in ["read", "write"]:
                permissions.append(token.text.lower())
        
        return {"action":action,"username": username, "permissions": permissions}

