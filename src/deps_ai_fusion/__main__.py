import click

from deps_ai_fusion.entrypoint import run_agent_api, run_api, run_message_dispatcher


@click.group()
def cli() -> None:
    pass


@click.command()
def serve() -> None:
    run_api()


@click.command()
def dispatch() -> None:
    run_message_dispatcher()


@click.command()
def agent() -> None:
    run_agent_api()


if __name__ == "__main__":
    cli.add_command(serve)
    cli.add_command(dispatch)
    cli.add_command(agent)
    cli()
