# MSPAF SNOP, the Silly-Named Opinion Parser

## About
MSPA SNOP is a Python 2.7 program created by Austin "Protractor Ninja" Anderson, designed to parse MSPA forum theads. Once known as vBullet! and designed to work with all vBulletin boards, its compatability scope became much more specific after I realized that not all vBulletin forums are equal and that trying to account for every possible style difference was probably a waste of time. As such, there are some remnants of all-inclusive compatibility scattered about, most notably in date and time parsing.

One of the most significant problems I ran into that caused me to adjust the scope of the project was that of understanding forum-inspecific BBCode elements. While there are some global codes like [code] and [quote], different versions appear to have differing implementations. Further, plugin-provided codes like `[spoiler]` don't necessarily follow the same conversion to HTML that the global codes do. I decided to focus purely on my reasons for writing the program - namely, MSPAF - but feel free to modify the code to support more forums. I'd love to see what you're able to do.

## Dependencies
Proper execution of MSPAF SNOP depends on the existence of external libraries not included in vanilla Python 2.7.3. These are:

- [lxml](http://lxml.de/) - for speedy XML comprehension
- [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) - for working effectively with the forum HTML tree

## License
vBullet! is licensed under a very simple BSD license. See vbullet-license.txt for details.