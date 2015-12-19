import re
import json
import requests
import sys
try:
    import vim
except:
    pass

API_KEY = "vYizAQxn)7tmkShJZyHqWQ(("


def strip_html(html):
    pattern = re.compile(r'<.*?>')
    return pattern.sub('', html)


def query_google(query, domain):
    payload = {
        'v': '1.0',
        'q': '%s:%s' % (query, domain)
    }
    url = "https://ajax.googleapis.com/ajax/services/search/web"
    try:
        response = requests.get(url, params=payload)
        data = json.loads(response.text)["responseData"]["results"]
    except:
        return None
    urls = []
    for result in data:
        url = result["url"]
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
    payload = {
        'order': '',
        'sort': 'votes',
        'site': 'stackoverflow',
        'key': API_KEY,
        'filter': '!)Q2B_4mND07Uc*hKpm6.P0Q5'
    }
    url = "https://api.stackexchange.com/2.2/questions/%s/answers"
    response = requests.get(url % qid, params=payload)
    return json.loads(response.text)["items"]


def parse_question_data(data, _filter):
    post = {
        "question": "",
        "answers": []
    }
    if len(data) == 0 or "title" not in data[0]:
        return post
    post["question"] = data[0]["title"]
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
    content = answer["body"]
    is_accepted = answer["is_accepted"]
    upvotes = answer["score"]
    url = answer["share_link"]
    return [content, url, is_accepted, upvotes, author]


def fetch_mass_data(query, _filter):
    urls = query_google(query, "www.stackoverflow.com")
    if urls is None:
        return None
    posts = []
    for url in urls:
        qid = get_question_id(url)
        if not qid:
            continue
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
    # Ensure that the global flag is off by default
    vim.command('setlocal nogdefault')
    # Replace 1-2 \r's with one.
    vim.command('silent %s/\r\{1,2\}/\r/ge')
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
            response.append(strip_html(answer[0]) + "\r")
    return response


def stackAnswersVim(query, _filter):
    query = vim.eval("a:2")
    _filter = vim.eval("g:stack_filter")
    data = fetch_mass_data(query, _filter)
    if data is None:
        text = ["Error fetching data...",
                "There are a few possibilities:",
                "1) You are not connected to the Internet",
                "2) Google has temporarily blocked your ip"
                ]
        _output_preview_text(text)
    else:
        _output_preview_text(_generate_stack_answers_format(data))


def stackAnswersCI(query, _filter):
    data = fetch_mass_data(query, _filter)
    if data is None:
        text = ["Error fetching data...",
                "There are a few possibilities:",
                "1) You are not connected to the Internet",
                "2) Google has temporarily blocked your ip"
                ]
        return text
    else:
        formatted = _generate_stack_answers_format(data)
        formatted = "\n".join(formatted)
        formatted = formatted.replace("\r", "\n")
        formatted = formatted.replace("\n\n", "\n")
        return formatted

if __name__ == "__main__":
    args = sys.argv
    if "--cli" in args:
        _filter = args[2]
        query = " ".join(args[3:])
        print stackAnswersCI(query, _filter)
