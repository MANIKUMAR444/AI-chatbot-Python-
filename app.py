from flask import Flask, render_template, request
from scraper import fetch_page_content, extract_article_text, summarize_content, answer_question
import validators

app = Flask(__name__)

# ✅ URL validation function
def is_valid_url(url):
    """Check if the provided URL is valid."""
    return validators.url(url)

@app.route("/", methods=["GET", "POST"])
def index():
    summary, answer, error = None, None, None

    if request.method == "POST":
        url = request.form.get("url")
        question = request.form.get("question")

        # ✅ Validate URL
        if url and is_valid_url(url):
            html_content = fetch_page_content(url)

            # ✅ Check if content is valid
            if html_content and "Error:" not in html_content:
                article_text = extract_article_text(html_content)

                if article_text and article_text != "No content found to extract.":
                    summary = summarize_content(article_text)

                    # ✅ If the user asks a question, generate an answer
                    if question:
                        answer = answer_question(article_text, question)
                else:
                    error = "No content found to extract and summarize."
            else:
                error = html_content
        else:
            error = "Please enter a valid URL starting with http:// or https://"

    return render_template(
        "index.html",
        summary=summary,
        answer=answer,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
