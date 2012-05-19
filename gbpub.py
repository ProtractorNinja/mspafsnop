# The Grand Battle to ePub Converterator!
# Obeys the PEP 8 Python "good practice" conventions. Ugh!
# Created by The Protractor Ninja

import re
import argparse

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

    # grand_battle = GrandBattle(thread_number)
    # compost_pile.write(grand_battle.soup.prettify("utf-8"))
    # print grand_battle.get_ranked_authors_list()
    # compost_pile.write(grand_battle.get_post(1).prettify("utf-8"))
    # compost_pile.write("~ ~ ~~~ NEXT LINE BEGINS GETCONTENT ~~~ ~ ~\n")
    # compost_pile.write(grand_battle.get_post_content(1).encode("utf-8"))
    # for string in grand_battle.get_post(1).stripped_strings:
    #    compost_pile.write("{0}\n".format(string.encode("utf-8")))
