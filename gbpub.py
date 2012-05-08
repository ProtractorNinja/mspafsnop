# The Grand Battle to ePub Converterator!
# Obeys the PEP 8 Python "good practice" conventions. Ugh!
# Created by The Protractor Ninja

import re
import argparse
import urllib2
from bs4 import BeautifulSoup, element


class Thread(object):
    """
    A class representing an MSPA forum thread and its respective posts.

    Note that post numbers begin at one, i.e. the original post is #1.
    """

    def __init__(self, thread_number):
        """
        Create a thread instance using the given thread number.

        If the thread number is bad, then a URLError will be raised.
        """
        try:
            html = urllib2.urlopen(r"http://www.mspaforums.com/printthread.php"
                                   r"?t={0}&pp=9999".format(thread_number))
        except urllib2.URLError as error:
            raise error
        self.soup = BeautifulSoup(html, "lxml")
        self._posts = self.soup.find_all("li", id=re.compile('post_.*'))
        self.author = self.get_author()
        self.total_posts = len(self._posts)

        # Create a dictionary mapping an author to a list containing the
        # post numbers of all of their posts.
        self._author_list = dict()
        for post in self._posts:
            author = self.get_author(post).lower()
            post_number = self.get_post_number(post)
            if author in self._author_list:
                self._author_list[author].append(post_number)
            else:
                self._author_list[author] = [post_number]

        # Create a list of authors in the thread, ordered by number of
        # posts made. The aforementioned _author_list dictionary cannot
        # be used because dictionaries do not have order.
        #
        # The author with the most posts will be listed first.
        self._author_ranks = []
        for author, post_numbers in iter(self._author_list.items()):
            self._author_ranks.append((author, len(post_numbers)))
        self._author_ranks = map(lambda x: x[0], sorted(self._author_ranks,
                                 key=lambda x: x[1], reverse=True))

    def get_author(self, post_number=1):
        """
        Find the author of a post.
        """
        post_number = self.validate_post_number(post_number)
        author = self.get_post(post_number).find("span", "username")
        if author:
            return str(author.get_text().strip().lower())
        else:
            return "~NULL AUTHOR {0}~".format(post_number)

    def get_post_number(self, post):
        """
        Determine the post number of a given post Tag.
        """
        return int(post['id'].replace("post_", ""))

    def get_post(self, post_number=1):
        """
        Get a Tag object for a post of given number.

        A negative number starts from the last post, i.e. -1 is the
        final post. An argument of 0 or 1 returns the first post.

        Returns the original post by default.
        """
        post_number = self.validate_post_number(post_number)
        if post_number <= 0:
            return self._posts[post_number]
        else:
            return self._posts[post_number - 1]

    def find_posts_by_author(self, author=None):
        """
        Find all posts by a given author.

        Returns an empty list if there are no posts by the given author.
        """
        if author is None:
            author = self.author
        author = author.lower()
        return map(lambda x: self.get_post(x), self.find_post_numbers_by_author
                                               (author))

    def find_post_numbers_by_author(self, author=None):
        """
        Find the numbers of all posts by a given author.

        Returns an empty list if there are no posts by the given author.
        """
        if author is None:
            author = self.author
        author = author.lower()
        post_list = []
        if author in self._author_list:
            post_list = self._author_list[author][:]
        return post_list

    def get_ranked_authors_list(self, *args):
        """
        Get a list of thread authors by decreasing post amount.

        Optionally, authors to ignore in this list may be passed in as
        arguments in the variable length argument format.
        """
        return filter(lambda arg: not arg in args, self._author_ranks)

    def get_post_content(self, post_number=1):
        """
        Get the text content of a post.

        Ignores extra author and date data, as well as spoiler tags and
        most HTML markup. Keeps <b> and <i> tags for future epub usage.

        Defaults to the first post if no post number is specified.
        """
        post_number = self.validate_post_number(post_number)
        post = self.get_post(post_number)
        post_content = post.find("blockquote", "restore")

        post_text = str(post_content)
        post_text = (post_text.replace("<b>", "~~~~~b~~~~~")
                              .replace("</b>", "~~~~~/b~~~~~"))
        post_text = (post_text.replace("<i>", "~~~~~i~~~~~")
                              .replace("</i>", "~~~~~/i~~~~~"))

        post_content = BeautifulSoup(post_text)
        post_text = post_content.get_text()
        post_text = (post_text.replace("~~~~~b~~~~~", "<b>")
                              .replace("~~~~~/b~~~~~", "</b>"))
        post_text = (post_text.replace("~~~~~i~~~~~", "<i>")
                              .replace("~~~~~/i~~~~~", "</i>"))
        return post_text

    def validate_post_number(self, post_number):
        """
        Determine if a "post number" is a post Tag or an integer.

        If the "number" is in fact a Tag, then return the post number
        corresponding to said Tag.
        """
        if type(post_number) is element.Tag:
            post_number = self.get_post_number(post_number)
        return post_number


class GrandBattle(Thread):
    """
    Represents an instance of an MSPAF Grand Battle, documenting rounds,
    players and their characters, narrator(s), and other information.

    Subclasses the Thread class to keep basic functions separate from
    specifically Thread-oriented functions.
    """

    def __init__(self, thread_number):
        super(GrandBattle, self).__init__(thread_number)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Absorb an MSPA Forum thread "
                                                 "and turn it into an ebook.")
    parser.add_argument('data', help="A MSPAF URL or thread ID number.")
    argument_data = parser.parse_args().data
    if re.match(r"^[\d]+$", argument_data):
        thread_number = argument_data
    else:
        url_test = re.match(r"https?://www\.mspaforums\.com/(?:show|print)"
                            r"thread\.php\?(?:t=)?([\d]+)", argument_data)
        if not url_test:
            raise ValueError("{0} is not a thread number or valid URL."
                             .format(argument_data))
        thread_number = url_test.group(1)

    # Open up a gateway to the compost pile file for testing!
    compost_pile = open("C:/users/austin/root/tmp/temp.txt", "w")

    grand_battle = GrandBattle(thread_number)
    #compost_pile.write(grand_battle.soup.prettify("utf-8"))
    #print grand_battle.get_ranked_authors_list()
    compost_pile.write(grand_battle.get_post(1).prettify("utf-8"))
    compost_pile.write("~ ~ ~~~ NEXT LINE BEGINS GETCONTENT ~~~ ~ ~\n")
    compost_pile.write(grand_battle.get_post_content(1).encode("utf-8"))
    #for string in grand_battle.get_post(1).stripped_strings:
    #    compost_pile.write("{0}\n".format(string.encode("utf-8")))
