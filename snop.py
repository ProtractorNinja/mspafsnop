# MSPAF SNOP
# MSPA Forums Silly-Named Opinion Parser
#!/usr/bin/env python

from datetime import timedelta, date, datetime
import copy
import re


class Author(dict):
    """
    A dict-like object representing an author in a vBulletin thread.

    Quick Function Reference:
    add_post(Post) -- Easily attribute a post to this author.

    Instance Attributes:
    is_op (bool) -- Whether or not this author started the thread.
    name (str) -- The author's user name.
    parent (Thread) -- The author's parent thread.
    posts (list) -- All of the author's Posts.
    post_numbers (list) -- All of the numbers of the author's Posts.

    The Author class works similarly to a dictionary; post numbers are
    keys that reference a Post object value. When testing for membership
    (e.g. while using the 'if Post in Author'), both post numbers and
    Post objects are acceptable search values.

    Author.posts and Author.post_numbers both return pre-sorted lists
    according to their member post numbers. To get a list ordered in the
    same manner as the Author object dictionary, use Author.keys() for
    post numbers or Author.values() for Post objects.

    """

    def __init__(self, author_name, parent_thread):
        """
        Create an author object using a user name and a parent thread.

        Positional Arguments:
        author_name (str) -- The author's given user name.
        parent_thread (Thread) -- The Thread that this author's posts
                                  are located in.

        """
        dict.__init__(self)
        self._name = author_name
        self._parent = parent_thread

    def add_post(self, post):
        """
        Attribute a Post to this author.

        This method is essentially a shorthand method for adding a post,
        ensuring that the dictionary value is added properly.

        """
        self[post.number] = post

    @property
    def is_op(self):
        """Test if this author is the Thread creator."""
        return 1 in self

    @property
    def name(self):
        """Get the name of the author."""
        return self._name

    @property
    def parent(self):
        """Get the parent Thread of this author."""
        return self._parent

    @property
    def posts(self):
        """
        Get a list of post objects contained in this author object.

        """
        return sorted(self.values())

    @property
    def post_numbers(self):
        """
        Get a list of post numbers contained in this author object.

        """
        return sorted(self.keys())

    # Sort-related function overrides
    def __eq__(self, other):
        """Determine if this author is the same as another"""
        return self.name == other.name

    def __ne__(self, other):
        """Determine if this author is not the same as another"""
        return self.name != other.name

    def __lt__(self, other):
        """
        Determine if this author has made fewer posts than another.

        """
        return len(self) < len(other)

    def __le__(self, other):
        """
        Determine if this author has made the same amount of or a lesser
        amount of posts than another user.

        """
        return len(self) <= len(other)

    def __gt__(self, other):
        """Determine if this author has made more posts than another."""
        return len(self) > len(other)

    def __ge__(self, other):
        """
        Determine if this author has made the same amount of or a
        greater amount of posts than another user.

        """
        return len(self) >= len(other)

    # Collection-related function overrides
    def __contains__(self, item):
        """
        Determine if this author has made a given post by number or
        Post object.

        """
        return item in self.keys() or item in self.values()


class Post(object):
    """
    An object representing a vBulletin forum post.

    Quick function reference:
    get_clean_content(**kwargs) -- Get a cleaned post content string.

    Instance Attributes:
    Post.author (Author) -- The post's author.
    Post.date (date) -- The date on which the post was made.
    Post.html (str) -- The post content's internal HTML.
    Post.number (int) -- The post number. First post number is 1.
    Post.parent (Thread) -- The parent Thread of this post.
    Post.tag (Tag) -- The BS4 tag representing the post's content.
    Post.time (time) -- The time at which the post was made.

    """

    def __init__(self, post_tag, parent_thread, date_format=None,
                 time_format=None):
        """
        Create a post object using data from a forum post HTML tag.

        Positional Arguments:
        post_tag (Tag) -- A BS4 Tag whose name should be "li" and whose
                          id attribute should be "post_" followed by a
                          number.
        parent_thread (Thread) -- The Thread that contains this post.

        Optional Arguments:
        date_format (str) -- A 'y-m-d' style string representing the
                             way the forum formats dates. None by
                             default.
        time_format (str) -- An 'm:s' style string representing the way
                             the forum formats time strings. None by
                             default.

        Raises:
        ValueError -- raised if a given date or time format string is
                      invalid for the string it tries to parse.

        date_format and time_format are unnecessary if the forum date
        and time are in the "friendly" (e.g. "5 minutes ago") format.
        Otherwise, if the formatting arguments' values are None, then
        date and time will not be calculated unless the date is given as
        "today" or "yesterday." Post object calls to date, time, and
        datetime will return None if so.

        Use the PHP date function documentation for string reference:
        http://php.net/manual/en/function.date.php

        Example:
        Say the post's post time data says "07 Mon 2012 18:22"
        A working call would be this:
        post = Post(tag, 'm D Y', 'g:i')

        Because some formats appear identical with certain numbers (like
        those that exclude a preceding zero) involved, examining more
        than one example string may be necessary to determine the
        correct format. The previous example also would have worked with
        'G:i' as the time_format argument, because there was no way to
        tell if an hour lower than 10 would have included a 0 (e.g.
        09:42 versus 9:42)

        """

        self._parent = parent_thread
        self._author = self._parent.get_author(str(post_tag.find("span",
                       "username").get_text().strip()))
        self._post_number = int(post_tag['id'].replace("post_", ""))
        self._post_tag = post_tag

        # We'll be modifying the content tag later on, so _o_content_tag
        # exists in case we want access to the unmodified original.
        self._content_tag = post_tag.find("blockquote", "restore")
        self._o_content_tag = copy.deepcopy(self._content_tag)

        # Create a pure HTML string representing the post's content
        self._html = "".join([str(child) for child in self._o_content_tag
                                                      .children])

        # HTML-to-effective-BBCode is probably broken but the concept is
        # there.

        # Find all the spoilers and replace the content with
        # <spoiler>...</spoiler>
        for spoiler in self._content_tag.find_all("div", "spoiler"):
            spoiler.parent.wrap(self._content_tag.new_tag("spoiler"))
            spoiler.div.decompose()
            spoiler.parent.div.decompose()
            spoiler.parent.unwrap()
            spoiler.unwrap()

        # Find bbcode_container elements (like Quotes and Code tags -
        # these are different in structure from spoilers, as spoilers
        # appear to be provided by a vBulletin plugin that does not
        # encode to HTML in the same way) and replace the tag with
        # <[bbcodename]>...</[bbcodename]>
        for bbelem in self._content_tag.find_all("div", "bbcode_container"):
            code_name = str(bbelem.div.extract().string)[:-1].lower()
            code_tag = bbelem.new_tag(code_name)
            code_has_author = bbelem.div.div.strong
            for hr in bbelem.find_all("hr"):
                hr.decompose()
            if code_has_author:
                code_tag['author'] = str(code_has_author.string)
                code_parent = bbelem.wrap(code_tag)
                bbelem.replace_with(bbelem.find("div", "message"))
                code_parent.find("div", "message").unwrap()
            else:
                bbelem.wrap(code_tag)
                bbelem.div.unwrap()
                bbelem.unwrap()

        # Date and time calculation begins with determining whether
        # or not the post date and time are formatted in the
        # "friendly" manner, e.g. "x minutes ago."
        datetime_string = post_tag.find("div", "datetime").get_text()
        if "ago" in datetime_string:
            date_data = datetime_string.split(" ")
            unit_type = date_data[1].lower()
            units = int(date_data[0])
            if "minute" in unit_type:
                post_datetime = datetime.now() - timedelta(minutes=units)
            elif "hour" in unit_type:
                post_datetime = datetime.now() - timedelta(hours=units)
            elif "day" in unit_type:
                post_datetime = datetime.now() - timedelta(days=units)
            elif "week" in unit_type:
                post_datetime = datetime.now() - timedelta(weeks=units)
            elif "year" in unit_type:
                post_datetime = datetime.now() - timedelta(years=units)
            else:
                post_datetime = datetime.now()

            self._date = post_datetime.date()
            self._time = post_datetime.time()
        else:
            # If the date & time formatting option for the forum isn't
            # on the friendly setting, date and time are always
            # separated by the character sequence ", ". Since the date
            # string might include the same sequence (e.g. if the format
            # was "Day, Month, Year"), after the string is split based
            # on ", " all of the strings except for the last one are
            # joined via the same sequence and the last is left alone.
            # This effectively splits one time starting at the end of
            # the string.
            datetime_list = datetime_string.split(", ")
            date_string = ", ".join(datetime_list[:-1])
            time_string = datetime_list[-1]

            if "today" in date_string:
                self._date = date.today()
            elif "yesterday" in date_string:
                self._date = date.today() - timedelta(days=1)
            elif not date_format is None:
                try:
                    self._date = (datetime.strptime(date_string,
                                 date_format).date())
                except ValueError:
                    raise ValueError("Date format '{0}' does not match string "
                                     "'{1}'.".format(date_format, date_string))
            else:
                self._date = None

            if not time_format is None:
                try:
                    self._time = (datetime.strptime(time_string, time_format)
                                 .time())
                except ValueError:
                    raise ValueError("Time format '{0}' does not match string "
                                     "'{1}'.".format(time_format, time_string))
            else:
                self._time = None

        self._author.add_post(self)

    def get_clean_content(self, **kwargs):
        """
        Get a cleaned-up, non-html version of a post's content.

        Optional Keyword Arguments:
        spoilers (bool) -- If True, remove all evidence of spoilers in
                           the post. If False, treat spoilered content
                           as if it were not contained in a spoiler.
                           Default is true.
        quotes (value) -- If True, remove all evidence of quotes in the
                          post. If False, treat quoted text as if it
                          were not quoted. If a str tuple or list, uses
                          the first two values to wrap the content.
                          Default is True.
        trim (bool) -- If true, cuts multiple newlines to a single
                       newline in the cleaned text. Default is true.
        ignoretags (list) -- A list of HTML tags to be ignored (that is,
                             *not* unwrapped to just text) in the
                             cleaning process. Default is None.
        regex (list) -- Removes all matches to the given regular
                        expression in the post. Default is None.

        """
        content = copy.deepcopy(self._o_content_tag)

        if kwargs.get("spoilers", True):
            for spoiler in content.find_all("div", "spoiler"):
                spoiler.parent.decompose()
        else:
            for spoiler in content.find_all("div", "spoiler"):
                spoiler.div.decompose()
                spoiler.parent.div.decompose()
                spoiler.parent.unwrap()
                spoiler.unwrap()

        quotes = kwargs.get("quotes", True)
        if type(quotes) is tuple or type(quotes) is list:
            pass
        elif quotes:
            pass
        else:
            pass

        ignoretags = kwargs.get("ignoretags", None)
        if ignoretags:
            pass

        # This is done AFTER just text is acquired
        regex = kwargs.get("regex", None)
        if regex:
            pass

        if kwargs.get("trim", False):
            pass

    @property
    def author(self):
        """Get the post's author."""
        return self._author

    @property
    def date(self):
        """
        Get the date on which the post was made.

        Returns a date object, unless there was a problem parsing a date
        object from the post, in which case a value of None is returned.

        """
        return self._date

    @property
    def html(self):
        """Get the pure HTML content of the post."""
        return self._html

    @property
    def content(self):
        """Get the pure HTML content of the post."""
        return self._html

    @property
    def number(self):
        """Get the post's number."""
        return self._post_number

    @property
    def parent(self):
        """Get the parent Thread of this post."""
        return self._parent

    @property
    def post_tag(self):
        """Get the post's BS4 tag."""
        return self._post_tag

    @property
    def tag(self):
        """Get the post's BS4 content-only tag."""
        return self._o_content_tag

    @property
    def time(self):
        """
        Get the time at which the post was made.

        Returns a time object, unless there was a problem parsing a time
        object from the post, in which case a value of None is returned.

        """
        return self._time

    # Sort-related function overrides
    def __eq__(self, other):
        """Determine if this post is the same as another."""
        return self._post_tag == other._post_tag

    def __ne__(self, other):
        """Determine if this post is not the same as another."""
        return self._post_tag != other._post_tag

    def __lt__(self, other):
        """Determine if this post comes before another."""
        return self._post_number < other._post_number

    def __le__(self, other):
        """Determine if this post comes before or is next to another."""
        return self._post_number <= other._post_number

    def __gt__(self, other):
        """Determine if this post comes after another."""
        return self._post_number > other._post_number

    def __ge__(self, other):
        """Determine if this post comes after or is next to another."""
        return self._post_number >= other._post_number
