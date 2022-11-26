# GitHub App Generator - Python based

This GitHub Actions leverages Python script and Docker container to generate GitHub App token based on your organization.

## How does this work?

Before getting any further, it will be good to have some understanding about GitHub App first.

To learn more about GitHub App, [please follow this guide](https://docs.github.com/en/enterprise-cloud@latest/developers/apps/getting-started-with-apps/about-apps). However, to give a little overview of how GitHub App can work for this automation, here is a short overview. GitHub App is an unique app that can be installed into GitHub organization(s) with granular permissions you can set to (1) listen to GitHub webhook events and/or (2) perform operations on GitHub resources like Pull Requests, Secrets, Issues, commits, etc. Although it is commonly thought as GitHub App needs to be created an application and to be deployed somewhere, GitHub App can generate this unique GitHub App token, which is like an OAuth token, to perform actions in behalf of a human user, meaning that you don't need to use Personal Access Token (PAT).

To talk to GitHub App, you need two things: GitHub App ID and GitHub PEM, which you can get by generating a GitHub App. These are is a GitHub Secret that you need to configure in your repository:

- `private-key` which you need to provide as a Secret

And you can pass these information as input values, but you can also read as environment values or Secrets.

- `app-id` which you can provide as either input or secrets
- `organization` which you can provide as either input or secrets

Python script generates JWT token with provided GitHub App ID and GitHub APP PEM to generate GitHub App Token and grab GitHub App installation id based on organization name and GitHub App token. Next, this script calls an endpoint that generated GitHub App based on temporary JWT token and GitHub App installation id. Lastly, Python script sets the output so it can be passed onto next GitHub Action job step.

## Prerequisites

- You created a GitHub App, installed into at least one organization, and have Application ID and PEM file from GitHub App
- You added GitHub Application PEM's content as a GitHub Secret. This needs be passed in your GitHub Action pipeline as `private-key`
- You have a repository with GitHub Actions and placed GitHub Action pipeline (see example)

## How to run

To call this action, you need to include `bryantson/github-app-token-generator` with whatever the version that you want to use. For example,

```yaml
uses: bryantson/github-app-token-generator@1.0
id: generate-token
with:
    app-id: ${{ github.event.inputs.app-id}}
    organization: ${{ github.event.inputs.organization }}
    private-key: ${{ secrets.PRIVATE_KEY }}
```

For values passing to `with` can come from user inputs, Secrets, or whatever, but the keys (`app-id`, `organization`, and `private-key`) have to match. Value of `id` can be a name that you want to call it, but you need to define it to pass the token to next step.

Then, you need to grab the output like this `${{ steps.generate-token.outputs.token }}`, for example.

See an example of a GitHub Actions pipeline like one below and placed under `.github/workflows` folder (e.g. `github/workflows/action-list-repos.yml`)

```yaml
name: List repositories based on GitHub App token

on:
  workflow_dispatch:
    inputs:
      app-id:
        required: true
        default: ''
        description: Application ID
      organization:
        required: true
        default: ''
        description: Organization

jobs:
  jwt-test-run:
    runs-on: ubuntu-latest
    name: Generate Token
    steps:

      - name: JWT Token
        uses: bryantson/github-app-token-generator@v1
        id: generate-token
        with:
          app-id: ${{ github.event.inputs.app-id}}
          organization: ${{ github.event.inputs.organization }}
          private-key: ${{ secrets.PRIVATE_KEY }}

      - name: List repositories in an organization
        run: |
          curl \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer $GH_TOKEN" \
            https://api.github.com/orgs/$ORG/repos
        env:
          GH_TOKEN: ${{ steps.generate-token.outputs.token }}
          ORG: ${{ github.event.inputs.organization }}
```

