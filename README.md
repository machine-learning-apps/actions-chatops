![Actions Status](https://github.com/machine-learning-apps/actions-chatops-workaround/workflows/Tests/badge.svg)

# Trigger Actions With ChatOps via PR Labels (Workaround For ChatOps)

This action helps you trigger downstream actions with a custom command made via a comment in a pull request, otherwhise known as [ChatOps](https://www.pagerduty.com/blog/what-is-chatops/).  This action is uses a GitHub App to make an issue label that then can trigger an Action.  This is alternative to the [this Action](https://github.com/marketplace/actions/chatops-for-actions) that uses authenticates as a seperate GitHub App that adds a label you specify to your pull request.  The benefits of this are two-fold:  (1) Unlike a PR-Comment which [triggers Actions workflows on the default branch](https://help.github.com/en/articles/events-that-trigger-workflows#issue-comment-event-issue_comment), the label event will trigger Actions to run on the branch of the PR.  (2) This can prevent you from accidentally executing the chatops command twice as the label event will not fire if the PR is already labeled. 

The reason this Action authenticates as a seperate GitHub app (whose authentication credentials you supply) is that you want the label applied on the PR to trigger downstream Actions and events created by GitHub Actions cannot trigger other Actions - therefore we use a GitHub App for this purpose.

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
    - required: true

  - `TEST_EVENT_PATH`:
    - description: An alternate place to fetch the payload for testing and debugging when making changes to this Action.  This is set to they system environment variable $GITHUB_EVENT_PATH by default.
    - require: false
    default: ""
