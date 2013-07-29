Bioannotator
============
A chrome extension that automatically links additional information to known known biological entities in papers. Currently it only operates on PLoS journals and only annotates known HGNC gene symbols.

TODO
----
* Support more journals.
* Support more types than gene symbols.
* Allow manual annotation of text.
* Detects if entity is defined as an abbreviation and don't highlight.
* Close popover on click of link or outside popover.
* Option to only annotate first instance of each entity.

Installation
------------
Currently, this is hosted on an Ubuntu 13.04 server. Flask powers a simple server that responds to ajax requests with a array of the words of the article. The dataset is stored in Redis and currently only occupies ~12M of memory and contains 113211 keys. Each entity is contained in bloom filter powered by pyreBloom. Response times for each article averages around 0.7s depending on the length of the input.

* Install build essentials.
* Install Redis.
* Install hiredis, pyreBloom dependency. (apt-get install libhiredis-dev)
* Clone this repo.
* Install requirements.
* Download the [hgnc gene names](ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc_complete_set.txt.gz) to the db folder.
* Run `db/load_db.py` to load redis with the hgnc data.
* Deploy or run a dev server.

Icon Attributions
-----------------
[Book](http://thenounproject.com/noun/book/#icon-No2051) designed by [Charles Riccardi ](http://thenounproject.com/noun/book/#icon-No2051) from The Noun Project.
[DNA](http://thenounproject.com/noun/dna/#icon-No3928) designed by [Darrin Higgins](http://thenounproject.com/noun/dna/#icon-No3928) from The Noun Project.
[GPS](http://thenounproject.com/noun/gps/#icon-No625) designed by [Edward Boatman](http://thenounproject.com/edward) from The Noun Project.

