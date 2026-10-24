CAREERBRIDGE AI - LOCAL SETUP

1. Extract this ZIP.
2. Open the extracted CareerBridge_AI_Full_Project folder in VS Code.
3. Open Terminal -> New Terminal.
4. Run:
   py -m pip install -r requirements.txt
   py app.py
5. Open this address in your browser:
   http://127.0.0.1:5000

IMPORTANT:
- Keep app.py and the templates folder in the same project folder.
- HTML files must be inside the folder named exactly: templates
- Do not copy Markdown fences such as ```html into files.
- This is a student prototype. Job links open external job searches; they are not verified live vacancies.
- Resume analyzer currently supports .txt files and checks keywords only.
- Before publishing online, set a strong SECRET_KEY and add production security protections.
