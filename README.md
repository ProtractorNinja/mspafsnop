Grand Battle ePub Generator -- GBPub
====================================

This script has been designed for two purposes. One was its practical purpose,
that is, creating an ePub book out of an MSPAF Grand Battle. The second was to
teach myself Git, which has proven itself a worthy adversary.

GBPub chiefly uses Beautiful Soup 4 for HTML parsing, which depends on lxml.
Furthermore, GBPub implements python-epub-builder as the primary means of
building an ePub file, which depends on Genshi, lxml (again), and epubcheck.

It is because of these things that I found out about easy_install.

I haven't included the epub builder script in this git repository due to 
uncertainty with licensing. I'll get to it later, I suppose, because for now
I'm only concerned with slaying Git and becoming its one true master.
