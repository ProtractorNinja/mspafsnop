# vBullet! vBulletin Thread Parser
#!/usr/bin/env python

from datetime import timedelta, date, datetime, time
import re


class Post(object):
    """
    An object representing a vBulletin forum post.

    """

    def __init__(self, post_tag, date_format=None, time_format=None):
        """
        Create a post object using data from a forum post HTML tag.

        Positional Arguments:
        post_tag -- A BS4 Tag object whose name should be "li" and whose
            id attribute should be "post_" followed by a number.

        Optional Arguments:
        date_format -- A 'y-m-d' style string representing the
            way the forum formats dates. None by default.
        time_format -- An 'm:s' style string representing the exact
            way the forum formats time strings. None by default.

        Raises:
        ValueError -- raised if a given date or time format string is
        invalid for the string it tries to parse.

        date_format and time_format are unnecessary if the forum date
        and time are in the "friendly" (e.g. "5 minutes ago") format.
        Otherwise, if the formatting arguments' values are None, then
        date and time will not be calculated unless the date is given as
        "today" or "yesterday." Post object calls to date, time, and
        datetime will return None if so.

        Use the PHP date function documentation for string reference.

        Example:
        Say the post's post time data says "07 Mon 2012 18:22"
        A working call would be this:
        post = Post(tag, 'm D Y', 'g:i')

        Because some formats are similar with certain numbers (like
        those that exclude a preceding zero), more than one example
        string may be necessary to determine the correct format. The
        previous time string example also would have worked with 'G:i',
        because there was not way to tell if an hour lower than 10 would
        have included a 0.

        """

        self._author = str(post_tag.find("span", "username").get_text()
            .strip())
        self._post_number = int(post_tag['id'].replace("post_", ""))
        self._post_tag = (post_tag.find("blockquote", "restore")
                          .replace_with_children())

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
            # separated by the character sequence ", ".
            #
            # However, the date string may include these characters as
            # well, so separating the datetime string based on ", " may
            # split the string in the wrong place. To account for this,
            # the datetime string is reversed and then split using the
            # first (which is actually the last in the non-reversed
            # string) instance of " ," (the separator, reversed), then
            # each entry in the new list is reversed to get the natural
            # ordering back.
            datetime_list = datetime_string[::-1].split(" ,", maxsplit=1)
            datetime_list = [lambda x: x[::-1] for x in datetime_list]
            date_string = datetime_list[0]
            time_string = datetime_list[1]

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

    def get_clean_content(self, **kwargs):
        """
        Get a cleaned-up, non-html version of a post's content.

        Optional Keyword Arguments:
        spoilers (bool) -- If true, remove all evidence of spoilers in
                           the post. Default is true.
        trim (bool) -- If true, cuts multiple newlines to a single
                       newline in the cleaned text. Default is true.
        ignoretags (list) -- A list of tags to be ignored (that is,
                             *not* unwrapped to just text) in the
                             cleaning process. Default is none.
        regex (list) -- Removes all matches to the given regular
                        expression in the post. Default is none.

        """

        if kwargs.get("spoilers", True):
            pass

        if kwargs.get("trim", False):
            pass

        if kwargs.get("ignoretags", None):
            pass

        if kwargs.get("regex", None):
            pass

    @property
    def author(self):
        """Get the post's author."""
        return self._author

    @property
    def number(self):
        """Get the post's number."""
        return self._post_number

    @property
    def date(self):
        """
        Get the date on which the post was made.

        Returns a date object, unless there was a problem parsing a date
        object from the post, in which case a value of None is returned.

        """
        return self._date

    @property
    def time(self):
        """
        Get the time at which the post was made.

        Returns a time object, unless there was a problem parsing a time
        object from the post, in which case a value of None is returned.

        """
        return self._time

    @property
    def html(self):
        """Get the pure HTML content of the post."""
        return str(self._post_tag)

    @property
    def tag(self):
        """Get the post's BS4 content tag."""
        return self._post_tag
