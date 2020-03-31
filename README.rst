Hyacinth
########

*A Python script to create flower bouquets*

This has been a fun little exercise. My first actual use of Docker, which I at first thought was going to take up some time but it turned out to take almost none.

The code as is requires Python 3.8 for a single use of a walrus operator to clean up the reading from ``stdin``. Nothing fancy, but it clarifies the intent of the read operation.

There is an ``input.txt`` that creates some designs and a flower stream with one design that I'm not 100% sure is legal, but *is* supported in this implementation::

    DL13

All this design needs is 13 large filler flowers. The specification syntax for the bouquet design lists flowers 1..N, but the textual constraints don't mention it, where they mention all the other constraints.


Thoughts and opportunities for improvement
==========================================

I haven't gotten around to it, but I imagine it should be reasonably easy to support species codes longer than a single character. Names even because why not. Some small alterations to the regular expressions should do the trick. In a terse protocol this would allow for more than 26 species of flowers, which seems like it might happen, especially over time as certain kinds of flowers go out of fashion.

Alluded to in the source code but not included in any manner is the idea of a smarter scoring function to pick filler flowers. I'm fairly happy with the current solution which first picks flowers not used by other designs and then a random sample with a bias to common flowers.

Currently this solution does a random sample twice, mainly because the code is slightly less of an ugly mess that way, but it could also be argued that it creates a more pleasing bouquet of alphabet flowers. A proper scoring function that creates a clear order of flowers to pick would be interesting, but could easily add a few hours to this exercise (the simple ``Counter`` would have to be replaced by a priority queue of sorts).

Error checking and alerting is missing and obviously would be rather important to have in any sort of production environment. However, without good specification and knowledge of the rest of the system, it's difficult to make a good choice when encountering an error. Bad flowers messages could be reported but otherwise treated as not received, bad designs should result in a user error without further interruption of the system. With more of an application ecosystem that becomes an option.

Another thing that could be considered is adding an additional layer of abstraction on top of the ``Pool``, which manages the various flower-size based pools. Currently when processing designs and flowers, the code selects the flower-size pool from a dictionary and adds stuff to that. A ``PoolManager`` class with two methods to add designs and flowers would allow for easier validation and fun things like telemetry.


Docker commands to get going
============================

Create a Docker image for this repository from the ``Dockerfile``::

    $ docker build -t hyacinth .

Run the Docker image with a specified input (enabling ``stdin``)::

    $ docker run -i hyacinth < input.txt