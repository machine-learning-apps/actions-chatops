FROM hamelsmu/chatops-workaround

LABEL "com.github.actions.name"="ChatOps Via PR Labels"
LABEL "com.github.actions.description"="Trigger PR labels with chatops and a GitHub App, which is a work-around to trigger downstream Actions with the right context."
LABEL "com.github.actions.icon"="message-square"
LABEL "com.github.actions.color"="blue"
LABEL "repository"="https://github.com/machine-learning-apps/actions-chatops-workaround"
LABEL "homepage"="http://github.com/actions"
LABEL "maintainer"="Hamel Husain <hamel.husain@gmail.com>"

ENTRYPOINT ["python",  "/label_app.py"]