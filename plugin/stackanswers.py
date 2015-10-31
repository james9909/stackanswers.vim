import json
import requests
import vim
from bs4 import BeautifulSoup

API_KEY = "vYizAQxn)7tmkShJZyHqWQ(("


def query_google(query, domain):
    search = "https://www.google.com/search?as_q="
    url = search + query + ":" + domain
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    links = soup.findAll("li", attrs={"class": "g"})
    urls = []
    for link in links:
        url = str(link.find("h3", attrs={"class": "r"}))
        index = url.find("url?q=http://")
        if index != -1:
            url = url[index+6:url.find("&")]
            if is_valid_url(url):
                urls.append(url)
    return urls


def get_question_id(url):
    try:
        qid = int(url.split("/")[-2])
    except:
        qid = None
    return qid


def is_valid_url(url):
    return "stackoverflow" in url and "/tagged/" not in url


def get_question_data(qid):
    response = requests.get("https://api.stackexchange.com/2.2/questions/%s/answers?order=&sort=votes&site=stackoverflow&key=%s&filter=!*K1kKw1QtFm(YMCQ" % (qid, API_KEY))
    return json.loads(response.text)["items"]


def parse_question_data(data, _filter):
    post = {
        "question": "",
        "answers": []
    }
    post["question"] = data[0]["title"]
    del data[0]
    for answer in data:
        answer_data = parse_answer(answer)
        if _filter == "accepted":
            if answer_data[2]:
                post["answers"].append(parse_answer(answer))
        elif _filter == "top":
            post["answers"].append(parse_answer(answer))
            break
        else:
            post["answers"].append(parse_answer(answer))
    return post


def parse_answer(answer):
    author = answer["owner"]["display_name"]
    content = answer["body_markdown"]
    is_accepted = answer["is_accepted"]
    upvotes = answer["score"]
    url = answer["share_link"]
    return [content, url, is_accepted, upvotes, author]


def fetch_mass_data(query, _filter):
    urls = query_google(query, "www.stackoverflow.com")
    posts = []
    for url in urls:
        qid = get_question_id(url)
        data = get_question_data(qid)
        posts.append(parse_question_data(data, _filter))
    return posts


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
    lines = [line.encode('utf-8').replace("\n", "\r") for line in lines]
    vim.current.buffer[:] = lines
    vim.command('silent %s/\r\+/\n/ge')
    vim.command('silent %s/\%x00/\r/ge')
    vim.command('setlocal nomodifiable')


def _generate_stack_answers_format(posts):
    response = []
    for post in posts:
        answers = len(post["answers"])
        # If there is no question, pass
        if post["question"] == "":
            continue

        question = "Q: " + post["question"]
        response.append(question)
        response.append("%d Answer(s)" % answers)
        for answer in post["answers"]:
            response.append("=" * 80)
            response.append(answer[1] + " Upvotes: " + str(answer[3]))
            response.append(answer[0] + "\r")
    return response


def stackAnswers(query, _filter):
    query = vim.eval("a:2")
    _filter = vim.eval("g:stack_filter")
    data = fetch_mass_data(query, _filter)
    _output_preview_text(_generate_stack_answers_format(data))
