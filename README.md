![Actions Status](https://github.com/machine-learning-apps/actions-chatops/workflows/Tests/badge.svg)

# Trigger Actions With ChatOps via PR Labels or Deployements


This action helps you trigger downstream actions with a custom command made via a comment in a pull request, otherwhise known as [ChatOps](https://www.pagerduty.com/blog/what-is-chatops/).  

Optionally, you may provide credentials to authenticate as a GitHub App and label an issue once a trigger phrase is detected.  Having another app other than the GitHub Action apply a label allows you to create a label event to trigger downstream Actions (since an Action cannot create events that trigger other Actions).


## Example Usage

```yaml
name: Demo
on: [issue_comment]

jobs:
  label-pr:
    runs-on: ubuntu-latest
    steps:
      - name: listen for PR Comments
        uses: machine-learning-apps/actions-chatops@master
        with:
          APP_PEM: ${{ secrets.APP_PEM }}
          APP_ID: ${{ secrets.APP_ID }}
          TRIGGER_PHRASE: "/test-trigger-comment"
          INDICATOR_LABEL: "test-label"
        env: # you must supply GITHUB_TOKEN
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

        # This step clones the branch of the PR associated with the triggering phrase, but only if it is triggered.
      - name: clone branch of PR
        if: steps.prcomm.outputs.TRIGGERED == 'true'
        uses: actions/checkout@master
        with:
          ref: ${{ steps.prcomm.outputs.SHA }}

        # This step is a toy example that illustrates how you can use outputs from the pr-command action
      - name: print variables
        if: steps.prcomm.outputs.TRIGGERED == 'true'
        run: echo "${USERNAME} made a triggering comment on PR# ${PR_NUMBER} for ${BRANCH_NAME}"
        env: 
          BRANCH_NAME: ${{ steps.prcomm.outputs.BRANCH_NAME }}
          PR_NUMBER: ${{ steps.prcomm.outputs.PULL_REQUEST_NUMBER }}
          USERNAME: ${{ steps.prcomm.outputs.COMMENTER_USERNAME }}
```


## Mandatory Inputs

  - `TRIGGER_PHRASE`: this is the phrase in a PR comment that you want to trigger downstream Actions.  Example - "/deploy-app-test"

## Optional Inputs

  If one of the below three arguments are provided, all three must be present. 

  - `INDICATOR_LABEL`: label that wil be added to the PR if a triggering comment is detected.  This is used to trigger downstream Actions with the right context of the PR.

  - `APP_PEM`: description: string version of your PEM file used to authenticate as a GitHub App.  _This is required if the input INDICATOR_LABEL is supplied._

  - `APP_ID`:your GITHUB App ID. _This is required if the input INDICATOR_LABEL is supplied._

  - `TEST_EVENT_PATH`: An alternate place to fetch the payload for testing and debugging when making changes to this Action.  This is set to they system environment variable $GITHUB_EVENT_PATH by default.


## Outputs

 - `TRAILING_LINE:`: the text that immediately follows the triggering phrase that is on the same line.  For example,  "/trigger-phrase foo bar\n next line" will emit the value "foo bar" This is intended to be used as arguments for downstream actions.

 - `TRAILING_TOKEN:`: this is the next token that immediately follows the triggering phrase that is on the same line.  For example,  "/trigger-phrase foo bar" will emit the value "foo". This is intended to be used as arguments for downstream actions.

 - `PULL_REQUEST_NUMBER`: the number of the pull request

 - `COMMENTER_USERNAME`: The GitHub username of the person that made the triggering comment in the PR.

 - `BRANCH_NAME`: The name of the branch corresponding to the PR.

 - `SHA`: The SHA of the branch on the PR at the time the triggering comment was made.

 - `BOOL_TRIGGERED`: true or false depending on if the trigger phrase was detected and this is a pull request.
