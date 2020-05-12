# Release Guide
The following guide was created to ease the release process and is
aimed at being explanatory for both technical individuals as well as those with less development experience.

# Table of Contents
1) [Prerequsites](#prerequisites)
    1) [Python](#python)
    2) [Node](#node)
    3) [Package Installers](#package-installers)
2) [Target of Release](#target-of-release)
3) [Release Candidate](#release-candidate)
4) [Sprint Meeting Demonstration](#sprint-meeting-demonstration)
    1) [Checking Out The Tag](#checking-out-the-tag)
    2) [Ensuring Functional Software](#ensuring-functional-software)
        1) [Back End](#back-end)
        2) [Front End](#front-end)
5) [Demonstrating](#demonstrating)
6) [Releasing](#releasing)
<a name="prerequisites"></a>
## Prerequisites
In order to make sure you can do everything necessary the following will have to be installed and available from the console:
- `git`
- `python`
- `npm`
- `node`
- `pip`

<a name="python"></a>
### Python
`Python 2` has been end of life for quite some time, and our software requires `python 3.7`.
[Here's where you can get it](https://www.python.org/downloads/release/python-377/)

<a name="node"></a>
### Node
Node is also required for the compiling and executing of our front end. [Here's where you can get it](https://nodejs.org/en/download/)

<a name="installers"></a>
### Package Installers
- `pip` is the python package installer, it will be necessary to have pip in order to
install dependencies
- `npm` is the package manager for node and will be necessary for the front end

Installing `python` usually means that `pip` is automatically installed. The same is true
for `npm` and `node`. So if you can execute `python` and `node` in the terminal, you're
probably ok.

<a name="target-of-release"></a>
## Target of Release
The target of the release is most likely going to be the `master` branch.
So we'll work with that.

Make sure all of the features for the sprint have been merged, and that the
checks for master have been carried out. These are all done automatically, however
its still a good idea to check and see the current status of the master
branch on our [Travis-CI dashboard](https://travis-ci.com/github/AMOS-5/infinitag/branches).

<a name="release-candidate"></a>
## Release Candidate
Once you've made sure that the branch is ready to go, go to the [releases page on
GitHub](https://github.com/AMOS-5/infinitag/releases) and [draft a new release](https://github.com/AMOS-5/infinitag/releases/new).

The tag name you will create for the release candidate is simply `sprint-xx-release-candidate`,
where `xx` is of course the spring number.

Make sure you fill in the release notes with the following changes:

1) Any new features
2) Changes to existing features
2) Any bug fixes
3) Any breaking changes

All of this can be done ahead of the sprint meeting.

<a name="sprint-meeting-demonstration"></a>
## Sprint Meeting Demonstration
Before the sprint meeting make sure you have done the following:
1) Created the release candidate
2) Checked out the tag
3) Made sure the software compiles and the tests all work

<a name="checking-out-the-tag"></a>
### Checking out the tag
In order to get the release candidate perform the following steps:

- `git fetch --all --tags`
- `git checkout tags/spring-xx-release-candidate -b spring-xx-release-candidate`

<a name="ensuring-functional-software"></a>
### Ensuring functional software
When you're on the release candidate tag the following should work:

<a name="back-end"></a>
#### Back End
- `pip install -r requirements.txt`
- `python app.py`
- `python -m unittest discover -s tests`

<a name="front-end"></a>
#### Front End
- `cd frontend`
- `npm ci`
- `npm run build:ci`

The `run build:ci` command will do the following:
1) Gets rid of any existing builds
2) Runs all tests
3) Builds the front end for production


Each one of these things should be performed the day before the sprint meeting by
the release manager in order to ensure a smooth release.

<a name="demonstrating"></a>
## Demonstrating
Once you're confident that all code compiles and all tests work, you can start the software
for the demonstration.

- `python app.py`
- `cd frontend`
- `ng serve`

Navigate to [localhost](http://localhost:4200) and you should see the app up and running!

You can now use this to demonstrate the features added to the software since
the last release.

## Releasing
After everyone is happy with release, navigate to the tag you've already created in GitHub.

`https://github.com/AMOS-5/infinitag/releases/edit/sprint-xx-release`

being sure to replace `xx` with the sprint number. You can then alter the name
of the tag to remove the `candidate` marker. This will create a new tag (the old
one will still be available), and the release is done. Congratulations.
