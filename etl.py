from BeautifulSoup import BeautifulSoup
import HTMLParser


def get_statuses_as_lines(wall_html):
    """Get all statuses from the wall.htm of downloaded
    fb data"""

    text = open(wall_html,"r").read()#.decode('string_escape')
    soup = BeautifulSoup(text)
    all_status = soup.findAll("div",{"class":"comment"})
    lines =  map(lambda x:x.text, all_status)
    parser = HTMLParser.HTMLParser()
    lines = filter(lambda x: not "thoguth" in x, lines) # remove one particular stupid status
    return map(lambda x: parser.unescape(x),lines)
