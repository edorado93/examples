import urllib2
import optparse
import feedparser

url = "http://export.arxiv.org/api/query?search_query=cat:{}+AND+all:{}&start={}&max_results={}"
cat_url = "http://export.arxiv.org/api/query?search_query=cat:{}&start={}&max_results={}"
feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'


def get_options():
    parser = optparse.OptionParser()
    parser.add_option('-c', type="int", dest="max_results", default=20000, help="The maximum number of articles to fetch.")
    parser.add_option('--cat', type='string', dest='category', help='Category of articles to be fetched', default="cs.AI")
    parser.add_option('--sub', type='string', dest='sub_category', help='Sub category of the articles to be searched', default="")
    options, args = parser.parse_args()
    return options


def fetch_next_batch(start, batch_size, options):
    if start == options.max_results:
        return False, None, None

    corpus = []
    try:
        api_call = url.format(options.category, options.sub_category, start, batch_size) if options.sub_category else cat_url.format(options.category, start, batch_size)
        print api_call
        data = urllib2.urlopen(api_call).read()
        parsed_data = feedparser.parse(data)

        if not parsed_data["entries"]:
            return False, None, corpus

        for entry in parsed_data["entries"]:
            title, summary = entry["title"], entry["summary_detail"]["value"]
            # corpus += "\n\n" + '-'*10 + title + '-'*10 + "\n\n" + summary
            corpus.append("\n\n" + summary + "\n\n")
    except Exception as e:
        print "Some exception came up. e = ", e

    return True, start+batch_size, corpus

if __name__ == "__main__":
    options = get_options()
    start = 0
    data = []
    while True:
        fetch_more, start, corpus = fetch_next_batch(start, 1000, options)
        if corpus:
            data.extend(corpus)
        if not fetch_more:
            break
    print "Done fetching all of the articles.", len(data)

    train = data[:8000]
    valid = data[8000:10000]
    test = data[10000:]

    with open("train.txt", "w") as f:
        for text in train:
            f.write(text)

    with open("validation.txt", "w") as f:
        for text in valid:
            f.write(text)

    with open("test.txt", "w") as f:
        for text in test:
            f.write(text)
