"""Main entrypoint to the site generation logic run on push to master."""


if __name__ == "__main__":
    import scripts.components.compendium
    import scripts.components.deviations
    import scripts.components.messages
    import scripts.components.leaderboards

    scripts.components.messages.download()
    scripts.components.compendium.download()
    scripts.components.deviations.download()
    scripts.components.leaderboards.download()
