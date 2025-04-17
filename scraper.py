import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ✅ Add your Hugging Face API Key here
HUGGINGFACE_API_KEY = "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"
SUMMARIZATION_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
QA_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# ------------------------------
# ✅ Fetch HTML Content from URL
# ------------------------------
def fetch_page_content(url):
    """Fetch HTML content using Selenium for JavaScript-heavy websites."""
    try:
        # Set Chrome options for headless mode
        options = Options()
        options.headless = True  # Run in headless mode (no browser UI)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Initialize Chrome driver
        driver = webdriver.Chrome(options=options)

        # Open the URL
        driver.get(url)

        # Add wait time to load JavaScript content
        import time
        time.sleep(5)  # Wait for 5 seconds to ensure the content loads

        # Get the page source
        html_content = driver.page_source
        driver.quit()

        return html_content

    except Exception as e:
        return f"Error: Unable to fetch content using Selenium. Details: {str(e)}"


# ------------------------------
# ✅ Extract Article Text
# ------------------------------
def extract_article_text(html_content):
    """Extract article text from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract paragraphs from the content
    paragraphs = soup.find_all("p")
    article_text = "\n".join([para.get_text() for para in paragraphs if para.get_text()])

    return article_text if article_text else "No content found to extract."


# ------------------------------
# ✅ Summarize Extracted Content
# ------------------------------
def summarize_content(text):
    """Summarize extracted content using Hugging Face API."""
    if not text.strip():
        return "No content found to summarize."

    # ✅ Limit the length to first 700 words
    trimmed_text = " ".join(text.split()[:700])  # Limiting to 700 words

    try:
        # ✅ Send a POST request to Hugging Face API
        response = requests.post(
            SUMMARIZATION_API_URL,
            headers=HEADERS,
            json={"inputs": trimmed_text, "parameters": {"max_length": 130, "min_length": 30, "do_sample": False}},
            timeout=180  # ⏱️ Increase timeout to 180 seconds
        )

        if response.status_code == 200:
            summary_data = response.json()
            if isinstance(summary_data, list) and "summary_text" in summary_data[0]:
                return summary_data[0]["summary_text"]
            else:
                return "Error: No summary generated. Please try again."
        else:
            return f"Error: Failed to generate summary. Details: {response.json()}"

    except Exception as e:
        return f"Error: Failed to generate summary. Details: {str(e)}"



# ------------------------------
# ✅ Answer User's Question
# ------------------------------
def answer_question(text, question):
    """Answer user questions based on scraped content using Hugging Face API."""
    if not text.strip() or not question.strip():
        return "No valid content or question found to answer."

    trimmed_text = " ".join(text.split()[:700])  # ✅ Limit content to 700 words

    API_URL_QA = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    HEADERS_QA = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    try:
        # ✅ Send POST request to Hugging Face for QA
        response = requests.post(
            API_URL_QA,
            headers=HEADERS_QA,
            json={"context": trimmed_text, "question": question},
            timeout=120
        )

        if response.status_code == 200:
            qa_data = response.json()
            if "answer" in qa_data and qa_data["answer"]:
                return qa_data["answer"]
            else:
                return "Sorry, I couldn't find a relevant answer in the content."
        else:
            return f"Error: Unable to process question. Details: {response.json()}"

    except Exception as e:
        return f"Error: Failed to generate an answer. Details: {str(e)}"


# ------------------------------
# ✅ Main Function to Integrate
# ------------------------------
def run_scraper(url, question=None):
    """Main function to fetch, summarize, and answer user questions."""
    html_content = fetch_page_content(url)
    if "Error" in html_content:
        return html_content

    # Extract and summarize content
    article_text = extract_article_text(html_content)
    summary = summarize_content(article_text)

    # Check if a question was provided and answer it
    if question:
        answer = answer_question(article_text, question)
        return {"summary": summary, "answer": answer}
    else:
        return {"summary": summary, "answer": None}

