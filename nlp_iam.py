import spacy
from spacy.matcher import Matcher

class NLP_IAM:
    nlp = spacy.load("en_core_web_sm")
    matcher = Matcher(nlp.vocab)

    pattern = [
    {"IS_ALPHA": False, "IS_ASCII": True, "TEXT": {"REGEX": "^[a-zA-Z0-9._]+$"}}
    ]
    matcher.add("USERNAME_PATTERN", [pattern])

    def extract_usernames(self,sentence):
        doc = self.nlp(sentence)
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            # Filter out any non-username spans
            if span.text.isalnum() or "_" in span.text or "." in span.text:
                return span.text

    def extract_info(self,nlp, prompt):
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
            elif token.text.lower() in ["read", "write"]:
                permissions.append(token.text.lower())

        return {"action": action, "username": self.extract_usernames(prompt), "permissions": permissions}
