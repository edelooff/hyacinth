Hyacinth
########

A Python script to design flower bouquets.


Docker commands to get going
============================

Create a Docker image for this repository from the ``Dockerfile``::

    $ docker build -t hyacinth .

Run the Docker image with a specified input (enabling ``stdin``)::

    $ docker run -i hyacinth < input.txt