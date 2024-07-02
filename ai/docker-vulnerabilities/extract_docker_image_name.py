from groq import Groq

client = Groq(api_key="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")

def extract_docker_image_name(prompt):
    end_prompt = "give me the docker image name only noting else from this sentence."
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}{end_prompt}",
                }
            ],
            model="llama3-8b-8192",
        )
    print(chat_completion.choices[0].message.content)


try_prompt = [
    "Scan ubuntu:latest image for vulnerabilities.",
    "Scan nginx:latest image for vulnerabilities.",
    "Analyze python:3.9 image for security issues.",
    "Check node:14 image for potential vulnerabilities.",
    "Inspect redis:6.2 image for any security flaws.",
    "Examine mysql:8.0 image for known vulnerabilities.",
    "Scan alpine:3.12 image for security threats.",
    "Analyze golang:1.16 image for vulnerabilities.",
    "Check mongo:4.4 image for potential security issues.",
    "Inspect jenkins:latest image for any vulnerabilities.",
    "Examine tomcat:9.0 image for known security risks."
]

for each in try_prompt:
    extract_docker_image_name(each)