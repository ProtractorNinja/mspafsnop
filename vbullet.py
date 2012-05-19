# vBullet! vBulletin Thread Parser
#!/usr/bin/env python

from bs4 import BeautifulSoup, element
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
            way the forum formats dates.
        time_format -- An 'm:s' style string representing the exact
            way the forum formats time strings.

        The optional arguments are only optional if dates are known to
        be in the "x units ago" format. Use the PHP date function
        documentation for string reference.

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

        try:
            self._author = str(post_tag.find("span", "username").get_text()
                .strip())
            self._post_number = int(post_tag['id'].replace("post_", ""))

            # If the date & time formatting option for the forum isn't
            # the "friendly" setting (i.e. "Two minutes ago"), date and
            # time are always separated by the character sequence ", ".
            #
            # However, the date string may include these characters as
            # well, so separating the datetime string based on ", " may
            # split the string in the wrong place. To account for this,
            # the datetime string is reversed and then split using the
            # first (which is actually the last in the non-reversed
            # string) instance of " ," (the separator, reversed), then
            # each entry in the new list is reversed to get the natural
            # ordering back.
            post_datetime = (post_tag.find("div", "datetime").get_text()[::-1]
                .split(" ,", maxsplit=1))
            post_datetime = [lambda x: x[::-1] for x in post_datetime]
            post_date = datetime[0]

            if "ago" in post_date:
                date_data = date.split(" ")
                unit_type = date_data[1].lower()
                units = int(date_data[0])
                if "minute" in unit_type:
                    self._datetime = datetime.now() - timedelta(minutes=units)
                elif "hour" in unit_type:
                    self._datetime = datetime.now() - timedelta(hours=units)
                elif "day" in unit_type:
                    self._datetime = datetime.now() - timedelta(days=units)
                elif "week" in unit_type:
                    self._datetime = datetime.now() - timedelta(weeks=units)
                elif "year" in unit_type:
                    self._datetime = datetime.now() - timedelta(years=units)
                else:
                    self._datetime = datetime.now()
            else:
                if "today" in date:
                    # Today's date calculation
                    pass
                elif "yesterday" in date:
                    # Yesterday's date calculation
                    pass
                elif not date_format is None:
                    # Attempt to calculate date from string
                    pass
                else:
                    # Use today or raise error
                    pass

                if not time_format is None:
                    # Attempt to calculate time from string
                    pass
                else:
                    # Use now or raise error
                    pass
        # Do this if the post isn't actually a post
        # Add error types for different things
        except:
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
    def datetime(self):
        """
        Get the date on and time at which the post was made.

        Returns a datetime object.

        """
        return self._datetime

    @property
    def date(self):
        """
        Get the date on which the post was made.

        Returns a date object.

        """
        return self._datetime.date()

    @property
    def time(self):
        """
        Get the time at which the post was made.

        Returns a time object.

        """
        return self._datetime.time()

    # get pure HTML content string (not including author etc)

    # get BS4 content tag

    # get clean content (*ignoretags, **flags)
        # Unwraps tags to text, does not unwrap ignored tags
        # flags:
            # spoilers, s = true :: removes spoilers
            # regex, r = <REGEX> :: removes matches, can take a list
            # trim, t = false :: doesn't cut multiple lines to single
