GenericSetup Product README

  Overview

    This product is a "cut-down" version of the CMFSetup product, shipped
    with CMF 1.5.x:  it removes all CMF dependencies.  In the ideal world,
    CMFSetup would depend on this product, and supply the CMF-specific bits
    (handlers for actions, types, workflows, etc.).

    This product provides a mini-framework for expressing the configured
    state of a Zope Site as a set of filesystem artifacts.  These artifacts
    consist of declarative XML files, which spell out the configuration
    settings for each "tool" in the site , and supporting scripts / templates,
    in their "canonical" filesystem representations.

  Configurations Included

    The 'setup_tool' knows how to export / import configurations and scripts
    for the following tools:

      - (x) removal / creation of specified tools

      - (x) itself :)

      - (x) the role / permission map on the "site" object (its parent)

      - (x) properties of the site object

  Extending The Tool

    Third-party products extend the tool by registering handlers for
    import / export of their unique tools.

  Glossary

    Site --
      The instance in the Zope URL space which defines a "zone of service"
      for a set of tools.

    Profile --
      A "preset" configuration of a site, defined on the filesystem

    Snapshot --
      "Frozen" site configuration, captured within the setup tool

    "dotted name" --
      The Pythonic representation of the "path" to a given function /
      module, e.g. 'Products.CMFSetup.utils.ConfiguratorBase'.
