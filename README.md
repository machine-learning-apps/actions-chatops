![Actions Status](https://github.com/machine-learning-apps/actions-chatops-workaround/workflows/Tests/badge.svg)

# Trigger Actions With ChatOps via PR Labels (Workaround For ChatOps)

This action helps you trigger downstream actions with a custom command made via a comment in a pull request, otherwhise known as [ChatOps](https://www.pagerduty.com/blog/what-is-chatops/).  This action is a workaround that uses a GitHub App to make an issue label that then can trigger an Action.

## Example Usage

```yaml
name: Demo
on: [issue_comment]

jobs:
  label-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@master
      - name: test
        uses: machine-learning-apps/actions-chatops-workaround@master
        with:
          APP_PEM: ${{ secrets.APP_PEM }}
          APP_ID: ${{ secrets.APP_ID }}
          TRIGGER_PHRASE: "/test-trigger-comment"
          INDICATOR_LABEL: "test-label"
```

A demonstration of this in action can be found on [this PR](https://github.com/machine-learning-apps/actions-chatops-workaround/pull/2).

## Mandatory Inputs

  - `APP_PEM`:
    - description: string version of your PEM file used to authenticate as a GitHub App
    - required: true

  - `APP_ID`:
    - description: you GITHUB App ID.
    - required: true

  - `TRIGGER_PHRASE`:
    - description: this is the phrase in a PR comment that you want to trigger downstream Actions.  Example - "/deploy-app-test"
    - required: true

  - `INDICATOR_LABEL`:
    - description: label that wil be added to the PR if a triggering comment is detected.  This is used to trigger downstream Actions with the right context of the PR.
    - required: false
    - default: ""

  - `TEST_EVENT_PATH`:
    - description: An alternate place to fetch the payload for testing and debugging when making changes to this Action.  This is set to they system environment variable $GITHUB_EVENT_PATH by default.
    - require: false
    - default: ""


## Outputs

 - `TRAILING_LINE:`
    - description: the text that immediately follows the triggering phrase that is on the same line.  For example,  "/trigger-phrase foo bar\n next line" will emit the value "foo bar" This is intended to be used as arguments for downstream actions.
 - `TRAILING_TOKEN:`
    - description: this is the next token that immediately follows the triggering phrase that is on the same line.  For example,  "/trigger-phrase foo bar" will emit the value "foo". This is intended to be used as arguments for downstream actions.
 - `BOOL_TRIGGERED:`
    - description: true or false depending on if the trigger phrase was detected and this is a pull request.
 - `PULL_REQUEST_NUMBER:`
    - description: the number of the pull request