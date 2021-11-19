# Roadmapper

Makes graphviz maps of github milestones

# How to make roadmaps

Use github milestones as "epics" i.e. a final state to be achieved.
Associate issues with the milestone (must be in the same repo) if you want.

Declare dependencies between milestones by adding the dep to the milestone description

`/depends org/repo/<number>` - note that milestone # != issue #

Run this script to get a `dot` file

# Prior Art

Heavily inspired by https://github.com/plan3/stoneboard
