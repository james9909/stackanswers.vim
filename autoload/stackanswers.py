from bs4 import BeautifulSoup
import re
import json
import requests
import sys
try:
    import vim
except:
    pass


def clean(string):
    return string.encode("ascii", "ignore").decode("ascii")


def query_google(query, domain):
    url = "http://www.google.com/search?q=site:%s+%s" % (domain, query)
    urls = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    questions = soup.findAll("h3", { "class": "r" })
    for question in questions:
        urls += [re.search("\?q=(.*?)&", item["href"]).group(1) for item in question.find_all("a", href=True)]
    return urls


def get_answers(url):
    data = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    all_posts = soup.findAll("div", { "class": "post-text" })
    if len(all_posts) == 0:
        return None

    data["title"] = clean(soup.find("a", { "class": "question-hyperlink" }).text)
    data["question"] = clean(all_posts[0].text)
    data["answers"] = []
    for x in range(1, len(all_posts)):
        data["answers"].append(clean(all_posts[x].text))
    return data


def fetch_answers(query):
    urls = query_google(query, "stackoverflow.com")
    if urls is None:
        return None
    answers = []
    for url in urls:
        if url.startswith("https"):
            responses = get_answers(url)

        if responses:
            answers.append(responses)

    return answers


# StackAnswers output ---------------------------------------------------------


def _goto_window_for_buffer(b):
    w = int(vim.eval('bufwinnr(%d)' % int(b)))
    vim.command('%dwincmd w' % w)


def _goto_window_for_buffer_name(bn):
    b = vim.eval('bufnr("%s")' % bn)
    return _goto_window_for_buffer(b)


def _output_preview_text(lines):
    _goto_window_for_buffer_name('__Answers__')
    vim.command('setlocal modifiable')
    lines = [clean(line).replace("\n", "\r") for line in lines]
    vim.current.buffer[:] = lines
    # Ensure that the global flag is off by default
    vim.command('setlocal nogdefault')
    # Replace 1-2 \r's with one.
    vim.command('silent %s/\r\{1,2\}/\r/ge')
    vim.command('setlocal nomodifiable')


def _generate_stack_answers_format(posts):
    response = []
    for post in posts:
        answers = len(post["answers"])

        question = "Q: " + post["title"]
        response.append(question)
        response.append(post["question"])
        response.append("%d Answer(s)" % answers)
        for answer in post["answers"]:
            response.append("=" * 80)
            response.append(answer + "\r")
        response.append("="*80)
        response.append("="*80)
    return response


def stackAnswersVim(query):
    query = vim.eval("a:2")
    data = fetch_answers(query)
    if data is None:
        text = ["Error fetching data..."]
        _output_preview_text(text)
    else:
        _output_preview_text(_generate_stack_answers_format(data))


def stackAnswersCI(query):
    data = fetch_answers(query)
    if data is None:
        text = ["Error fetching data..."]
        return text
    else:
        formatted = _generate_stack_answers_format(data)
        formatted = "\n".join(formatted)
        formatted = formatted.replace("\r", "\n")
        return formatted

if __name__ == "__main__":
    args = sys.argv
    if "--cli" in args:
        query = " ".join(args[2:])
        print(stackAnswersCI(query))
