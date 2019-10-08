![Actions Status](https://github.com/machine-learning-apps/actions-chatops-workaround/workflows/Tests/badge.svg)

# Trigger Actions With ChatOps via PR Labels or Deployements

This action helps you trigger downstream actions with a custom command made via a comment in a pull request, otherwhise known as [ChatOps](https://www.pagerduty.com/blog/what-is-chatops/). This Action is similar to [this chatops action](https://github.com/machine-learning-apps/actions-chatops), except that this Action can defer to GitHub App to (1) Make labels on a PR or (2) Create a [Deployment](https://developer.github.com/v3/repos/deployments/#create-a-deployment).  The reasons you might want to do this are the following:  

- By deferring to a GitHub App to create a pull request label or a deployment event, you can trigger a downstream GitHub Action that runs in the context of a pull request.  The reason for using a GitHub App is Actions cannot trigger other Actions.  
- It can be important to run in the context of a pull request as that is the only way you will see [Check Runs](https://developer.github.com/v3/checks/runs/) for your pull request, so you can monitor the status of your workflows.   
  - Note that comments on PRs [triggers Actions workflows on the default branch](https://help.github.com/en/articles/events-that-trigger-workflows#issue-comment-event-issue_comment) which is not desireable for ChatOps most of the time.  This Action resolves this issue by piggybacking on a GitHub app to create an event that will trigger Actions workflows on the pull request's branch instead.
- This can prevent you from accidentally executing the chatops command twice as the label event will not fire if the PR is already labeled or the deployment has already been created.

Therefore, one of the required inputs is the secret key `APP_PEM` for authenticating as a GitHub App which has the following permissions:
- [Deployment](https://developer.github.com/v3/apps/permissions/#permission-on-deployments): read & write
- [Pull Requests](https://developer.github.com/v3/apps/permissions/#permission-on-pull-requests): read & write


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
