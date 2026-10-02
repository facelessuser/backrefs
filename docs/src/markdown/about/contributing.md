---
icon: lucide/users
---
# Contributing &amp; Support

## Overview

Contribution from the community is encouraged and can be done in a variety of ways:

-   Bug reports.
-   Reviewing code.
-   Code patches via pull requests.
-   Documentation improvements via pull requests.
-   Become a sponsor.

## Become a Sponsor :octicons-heart-fill-16:{: .heart-throb}

Open source projects take time and money. Help support the project by becoming a sponsor. You can add your support at
any tier you feel comfortable with. No amount is too little. We also accept one time contributions via PayPal.

[:octicons-mark-github-16: GitHub Sponsors](https://github.com/sponsors/facelessuser){: .md-button .md-button--primary }
[:fontawesome-brands-paypal: PayPal](https://www.paypal.me/facelessuser){ .md-button}

## Bug Reports

1.  Please **read the documentation** and **search the issue tracker** to try to find the answer to your question
    **before** posting an issue.

2.  When creating an issue on the repository, please provide as much info as possible:

    -   Version being used.
    -   Operating system.
    -   Errors in console.
    -   Detailed description of the problem.
    -   Examples for reproducing the error.  You can post pictures, but if specific text or code is required to
        reproduce the issue, please provide the text in a plain text format for easy copy/paste.

    The more info provided the greater the chance someone will take the time to answer, implement, or fix the issue.

3.  Be prepared to answer questions and provide additional information if required.  Issues in which the creator refuses
    to respond to follow up questions will be marked as stale and closed.

## Reviewing Code

Take part in reviewing pull requests and/or reviewing direct commits.  Make suggestions to improve the code and discuss
solutions to overcome weakness in the algorithm.

## Answer Questions in Issues

Take time and answer questions and offer suggestions to people who've created issues in the issue tracker. Often people
will have questions that you might have an answer for.  Or maybe you know how to help them accomplish a specific task
they are asking about. Feel free to share your experience to help others.

## Pull Requests

Pull requests are welcome, and if you plan on contributing directly to the code, there are a couple of things to be
mindful of.

Continuous integration tests on are run on all pull requests and commits via Travis CI.  When making a pull request, the
tests will automatically be run, and the request must pass to be accepted.  You can (and should) run these tests before
pull requesting.  If it is not possible to run these tests locally, they will be run when the pull request is made, but
it is strongly suggested that requesters make an effort to verify before requesting to allow for a quick, smooth merge.

### Running Validation Tests

In order to preserve good code health, a test suite has been put together with `pytest` (@pytest-dev/pytest). There are
currently two kinds of tests: syntax and targeted.  To run these tests, you can use the following command:

If you wish to run the tests locally, just run:

```console
$ hatch run +py=3.14 dev:tests
```

Coding standards are enforced using @astral-sh/ruff. The environment can be setup and run as shown below.

```console
$ hatch run +py=3.14 dev:lint
```

We use @python/mypy to enforce typing. It can be run as shown below.

```console
$ hatch run +py=3.14 dev:mypy
```

## Documentation Improvements

A ton of time has been spent not only creating and supporting this plugin, but also spent making this documentation.  If
you feel it is still lacking, show your appreciation for the plugin by helping to improve the documentation.  Help with
documentation is always appreciated and can be done via pull requests.  There shouldn't be any need to run validation
tests if only updating documentation.

Documents are in Markdown (with some additional syntax) and converted to HTML via Python Markdown and this extension
bundle. The documentation site is built with @zensical/zensical.

To build docs:

```console
$ hatch run docs:build
```

To serve docs and to live preview in a browser:

```console
$ hatch run docs:serve
```

To clean the documents:

```console
$ hatch run docs:clean
```
