FROM python:3-slim-stretch

RUN pip3 install requests github3.py jwt cryptography pyjwt

COPY label_app.py /
COPY tests/pr_comment_payload.json tests/

CMD python /label_app.py

ENTRYPOINT ["python",  "/label_app.py"]
