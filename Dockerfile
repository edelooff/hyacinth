# Hyacinth application container definition

FROM python:3
ADD hyacinth.py /
CMD [ "python", "./hyacinth.py" ]
