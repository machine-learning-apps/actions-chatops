#!/bin/bash
docker build -t hamelsmu/chatops -f prebuild.Dockerfile .

INPUT_TRIGGER_PHRASE="/test-trigger-comment"
INPUT_INDICATOR_LABEL="test-successfull"
TEST_EVENT_PATH="tests/pr_comment_payload.json"
GITHUB_REPOSITORY="machine-learning-apps/actions-ml-cicd"

docker push hamelsmu/chatops

docker run \
-e INPUT_TRIGGER_PHRASE=$INPUT_TRIGGER_PHRASE \
-e INPUT_INDICATOR_LABEL="$INPUT_INDICATOR_LABEL" \
-e INPUT_APP_PEM="${INPUT_APP_PEM}" \
-e INPUT_APP_ID="$INPUT_APP_ID" \
-e INPUT_TEST_EVENT_PATH="${TEST_EVENT_PATH}" \
-e GITHUB_REPOSITORY="$GITHUB_REPOSITORY" \
hamelsmu/chatops